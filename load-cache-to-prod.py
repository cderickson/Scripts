#!/usr/bin/env python3
"""
Production cache loader for reference datasets.

This script is intentionally standalone so it can be copied and executed from a
folder that contains the auxiliary files:
  - ALLDECKS (or ALL_DECKS)
  - MULTIFACED_CARD.txt (or MULTIFACED_CARDS.txt)
  - INPUT_OPTIONS.txt (or INPUT_OPTIONS_new.txt)

It upserts into production Postgres tables:
  - multifaced_cards
  - input_options
  - all_decks
"""

from __future__ import annotations

import argparse
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy import JSON, Column, MetaData, String, Table, create_engine
from sqlalchemy.dialects.postgresql import insert

ALLOWED_MULT_TYPES = {"SPLIT", "TRANSFORM", "DFC", "MDFC", "ADVENTURE"}

def dedupe_keep_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output

def parse_multifaced_cards(path: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    current_type: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue

        upper = line.upper()
        if upper in ALLOWED_MULT_TYPES:
            current_type = upper
            continue

        if current_type and " // " in line:
            front_nm, back_nm = (token.strip() for token in line.split(" // ", 1))
            rows.append((front_nm, back_nm, current_type))

    return list(dict.fromkeys(rows))

def parse_input_options(path: Path) -> list[tuple[str, str, list[str]]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    rows: list[tuple[str, str, list[str]]] = []

    idx = 0
    total = len(lines)
    while idx < total:
        while idx < total and (not lines[idx] or lines[idx].startswith("-")):
            idx += 1
        if idx >= total:
            break
        table_nm = lines[idx]
        idx += 1

        while idx < total and (not lines[idx] or lines[idx].startswith("-")):
            idx += 1
        if idx >= total:
            break
        var_nm = lines[idx]
        idx += 1

        while idx < total and (not lines[idx] or lines[idx].startswith("-")):
            idx += 1

        options: list[str] = []
        while idx < total and not lines[idx].startswith("-"):
            if lines[idx]:
                options.append(lines[idx])
            idx += 1

        rows.append((table_nm, var_nm, dedupe_keep_order(options)))

    return rows

def parse_all_decks(path: Path) -> list[tuple[str, str, str, list[str]]]:
    data = pickle.loads(path.read_bytes())
    if not isinstance(data, dict):
        raise ValueError("ALLDECKS payload is not a dictionary.")

    rows: list[tuple[str, str, str, list[str]]] = []
    for yyyy_mm, deck_rows in data.items():
        if not isinstance(deck_rows, list):
            continue
        for row in deck_rows:
            if not isinstance(row, (list, tuple)) or len(row) < 3:
                continue

            deck_nm = str(row[0]).strip()
            format_nm = str(row[1]).strip()
            deck_cards = row[2]

            if isinstance(deck_cards, set):
                deck_lst = sorted(str(card) for card in deck_cards)
            elif isinstance(deck_cards, (list, tuple)):
                deck_lst = [str(card) for card in deck_cards]
            else:
                deck_lst = [str(deck_cards)]

            rows.append((str(yyyy_mm).strip(), deck_nm, format_nm, deck_lst))

    return rows

def resolve_required_file(aux_dir: Path, candidates: list[str]) -> Path:
    for filename in candidates:
        candidate = aux_dir / filename
        if candidate.exists():
            return candidate
    joined = ", ".join(candidates)
    raise FileNotFoundError(f"Missing required file in {aux_dir}: expected one of [{joined}]")

def _read_key_from_credentials_file(path: Path, key: str) -> str:
    if not path.exists() or not path.is_file():
        return ""
    key_upper = key.upper()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        left, right = line.split("=", 1)
        normalized_left = left.strip().lstrip("\ufeff").upper()
        if normalized_left != key_upper:
            continue
        value = right.strip().strip('"').strip("'")
        if value:
            return value
    return ""

def resolve_database_url(cli_database_url: str | None, aux_dir: Path) -> str:
    if cli_database_url and str(cli_database_url).strip():
        return str(cli_database_url).strip()

    env_value = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    if env_value and str(env_value).strip():
        return str(env_value).strip()

    candidate_paths = [
        aux_dir / "_credentials.txt",
        Path.cwd() / "_credentials.txt",
        Path(__file__).resolve().parent / "_credentials.txt",
    ]
    for candidate in candidate_paths:
        creds_value = _read_key_from_credentials_file(candidate, "MOX_DATA_DB_URL")
        if creds_value:
            return creds_value
    return ""

def validate_lengths(
    multifaced_rows: list[tuple[str, str, str]],
    input_rows: list[tuple[str, str, list[str]]],
    all_decks_rows: list[tuple[str, str, str, list[str]]],
) -> None:
    if any(len(front_nm) > 50 or len(back_nm) > 50 for front_nm, back_nm, _ in multifaced_rows):
        raise ValueError("MULTIFACED_CARD values exceed max length (50).")

    if any(mult_type not in ALLOWED_MULT_TYPES for _, _, mult_type in multifaced_rows):
        raise ValueError("MULTIFACED_CARD contains unsupported mult_type values.")

    if any(len(table_nm) > 20 or len(var_nm) > 40 for table_nm, var_nm, _ in input_rows):
        raise ValueError("INPUT_OPTIONS table_nm/var_nm exceeds configured column lengths.")

    if any(len(yyyy_mm) > 7 or len(deck_nm) > 75 or len(format_nm) > 30 for yyyy_mm, deck_nm, format_nm, _ in all_decks_rows):
        raise ValueError("ALLDECKS contains values exceeding configured column lengths.")

def chunked_rows(rows: list[dict], size: int = 1000) -> Iterable[list[dict]]:
    for i in range(0, len(rows), size):
        yield rows[i : i + size]

def find_duplicate_rows(rows: list[dict], key_fields: list[str]) -> dict[tuple, list[dict]]:
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        groups.setdefault(key, []).append(row)
    return {key: grouped_rows for key, grouped_rows in groups.items() if len(grouped_rows) > 1}

def duplicate_rows_to_skip_count(duplicate_map: dict[tuple, list[dict]]) -> int:
    # For each duplicate key group, one row is kept and the rest would be skipped.
    return sum(len(rows) - 1 for rows in duplicate_map.values())


def build_duplicate_report_lines(table_name: str, duplicate_map: dict[tuple, list[dict]]) -> list[str]:
    lines: list[str] = []
    if not duplicate_map:
        lines.append(f"No duplicate keys found in {table_name}.")
        return lines

    skipped_rows = duplicate_rows_to_skip_count(duplicate_map)
    lines.append(f"Duplicate keys found in {table_name}: {len(duplicate_map)} key(s)")
    lines.append(f"Rows that would be skipped in {table_name}: {skipped_rows}")
    for key, rows in duplicate_map.items():
        lines.append(f"  Key={key} appears {len(rows)} times")
        for idx, row in enumerate(rows, start=1):
            if table_name == "all_decks":
                preview_row = {
                    "yyyy_mm": row["yyyy_mm"],
                    "deck_nm": row["deck_nm"],
                    "format_nm": row["format_nm"],
                    "deck_lst_len": len(row["deck_lst"]),
                }
            else:
                preview_row = row
            lines.append(f"    Row {idx}: {preview_row}")
    return lines

def main() -> None:
    parser = argparse.ArgumentParser(description="Upsert reference cache files into production database.")
    parser.add_argument(
        "--database-url",
        default=None,
        help=(
            "Production Postgres SQLAlchemy URL. "
            "Resolution order: --database-url, env DATABASE_URL/SQLALCHEMY_DATABASE_URI, "
            "then MOX_DATA_DB_URL from _credentials.txt."
        ),
    )
    parser.add_argument(
        "--aux-dir",
        default=".\\auxiliary\\",
        help="Directory containing ALLDECKS, MULTIFACED_CARD.txt, and INPUT_OPTIONS.txt (default: current directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate inputs, print counts, and exit without writing to the database.",
    )
    args = parser.parse_args()
    aux_dir = Path(args.aux_dir).resolve()
    db_url = resolve_database_url(args.database_url, aux_dir)

    multifaced_path = resolve_required_file(aux_dir, ["MULTIFACED_CARD.txt", "MULTIFACED_CARDS.txt"])
    input_options_path = resolve_required_file(aux_dir, ["INPUT_OPTIONS_new.txt", "INPUT_OPTIONS.txt"])
    all_decks_path = resolve_required_file(aux_dir, ["ALLDECKS", "ALL_DECKS"])

    multifaced_rows = parse_multifaced_cards(multifaced_path)
    input_rows = parse_input_options(input_options_path)
    all_decks_rows = parse_all_decks(all_decks_path)
    validate_lengths(multifaced_rows, input_rows, all_decks_rows)

    multifaced_payload = [
        {"front_nm": front_nm, "back_nm": back_nm, "mult_type": mult_type}
        for front_nm, back_nm, mult_type in multifaced_rows
    ]
    input_payload = [
        {"table_nm": table_nm, "var_nm": var_nm, "options_lst": options_lst}
        for table_nm, var_nm, options_lst in input_rows
    ]
    all_decks_payload = [
        {"yyyy_mm": yyyy_mm, "deck_nm": deck_nm, "format_nm": format_nm, "deck_lst": deck_lst}
        for yyyy_mm, deck_nm, format_nm, deck_lst in all_decks_rows
    ]

    if args.dry_run:
        multifaced_dupes = find_duplicate_rows(multifaced_payload, ["front_nm", "back_nm", "mult_type"])
        input_dupes = find_duplicate_rows(input_payload, ["table_nm", "var_nm"])
        all_decks_dupes = find_duplicate_rows(all_decks_payload, ["yyyy_mm", "deck_nm", "format_nm"])
        multifaced_skips = duplicate_rows_to_skip_count(multifaced_dupes)
        input_skips = duplicate_rows_to_skip_count(input_dupes)
        all_decks_skips = duplicate_rows_to_skip_count(all_decks_dupes)
        total_skips = multifaced_skips + input_skips + all_decks_skips

        print("Dry run complete. No database changes were made.")
        print(f"Would upsert {len(multifaced_payload)} rows into multifaced_cards")
        print(f"Would upsert {len(input_payload)} rows into input_options")
        print(f"Would upsert {len(all_decks_payload)} rows into all_decks")
        print(f"Duplicate keys in multifaced_cards: {len(multifaced_dupes)}")
        print(f"Duplicate keys in input_options: {len(input_dupes)}")
        print(f"Duplicate keys in all_decks: {len(all_decks_dupes)}")
        print(f"Rows that would be skipped in multifaced_cards: {multifaced_skips}")
        print(f"Rows that would be skipped in input_options: {input_skips}")
        print(f"Rows that would be skipped in all_decks: {all_decks_skips}")
        print(f"Total rows that would be skipped: {total_skips}")

        logs_dir = aux_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        report_path = logs_dir / f"load_cache_duplicate_report_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        report_lines: list[str] = [
            "Duplicate key report (would cause ON CONFLICT batch errors):",
            "",
        ]
        report_lines.extend(build_duplicate_report_lines("multifaced_cards", multifaced_dupes))
        report_lines.append("")
        report_lines.extend(build_duplicate_report_lines("input_options", input_dupes))
        report_lines.append("")
        report_lines.extend(build_duplicate_report_lines("all_decks", all_decks_dupes))
        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print(f"Wrote duplicate report to: {report_path}")
        return

    if not db_url:
        raise SystemExit("Missing database URL. Pass --database-url or set DATABASE_URL.")
    if db_url.lower().startswith("sqlite"):
        raise SystemExit("Refusing to run against SQLite. This script is production/Postgres only.")

    engine = create_engine(db_url, future=True, pool_pre_ping=True)
    metadata = MetaData()

    multifaced_cards = Table(
        "multifaced_cards",
        metadata,
        Column("front_nm", String(50), primary_key=True),
        Column("back_nm", String(50), primary_key=True),
        Column("mult_type", String(20), primary_key=True),
    )
    input_options = Table(
        "input_options",
        metadata,
        Column("table_nm", String(20), primary_key=True),
        Column("var_nm", String(40), primary_key=True),
        Column("options_lst", JSON, nullable=False),
    )
    all_decks = Table(
        "all_decks",
        metadata,
        Column("yyyy_mm", String(7), primary_key=True),
        Column("deck_nm", String(75), primary_key=True),
        Column("format_nm", String(30), primary_key=True),
        Column("deck_lst", JSON, nullable=False),
    )

    with engine.begin() as conn:
        for batch in chunked_rows(multifaced_payload):
            stmt = insert(multifaced_cards).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=["front_nm", "back_nm", "mult_type"],
                set_={"mult_type": stmt.excluded.mult_type},
            )
            conn.execute(stmt)

        for batch in chunked_rows(input_payload):
            stmt = insert(input_options).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=["table_nm", "var_nm"],
                set_={"options_lst": stmt.excluded.options_lst},
            )
            conn.execute(stmt)

        for batch in chunked_rows(all_decks_payload):
            stmt = insert(all_decks).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=["yyyy_mm", "deck_nm", "format_nm"],
                set_={"deck_lst": stmt.excluded.deck_lst},
            )
            conn.execute(stmt)

    print(f"Upserted {len(multifaced_payload)} rows into multifaced_cards")
    print(f"Upserted {len(input_payload)} rows into input_options")
    print(f"Upserted {len(all_decks_payload)} rows into all_decks")
    print("Done.")

if __name__ == "__main__":
    main()