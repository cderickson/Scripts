import argparse
from pathlib import Path
from typing import Dict, List
import requests

DEFAULT_TYPES = ["split", "transform", "dfc", "mdfc", "adventure"]
DEFAULT_OUTPUT = str(Path(__file__).resolve().parent / "auxiliary" / "MULTIFACED_CARDS.txt")

def _fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def fetch_multifaced_cards(card_types: List[str]) -> Dict[str, Dict[str, str]]:
    all_cards: Dict[str, Dict[str, str]] = {}

    for card_type in card_types:
        card_dict: Dict[str, str] = {}
        print(f"[start] type={card_type}")
        url = (
            f"https://api.scryfall.com/cards/search"
            f"?q=is%3A{card_type}+&unique=cards&order=name"
        )
        page_num = 1

        while True:
            print(f"[fetch] type={card_type} page={page_num}")
            content = _fetch_json(url)
            page_cards = content.get("data", [])
            print(f"[page] type={card_type} page={page_num} api_cards={len(page_cards)}")
            for card in page_cards:
                name = card.get("name", "")
                if " // " not in name:
                    continue
                if name.count(" // ") > 1:
                    continue
                front, back = name.split(" // ", 1)
                if front != back:
                    card_dict[front] = back

            if content.get("has_more"):
                url = content["next_page"]
                page_num += 1
            else:
                break

        all_cards[card_type] = card_dict
        print(f"[done] type={card_type} unique_multifaced={len(card_dict)}")

    return all_cards

def write_output(output_path: str, cards_by_type: Dict[str, Dict[str, str]]) -> None:
    print(f"[write] output={output_path}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as txt:
        for card_type, cards in cards_by_type.items():
            txt.write(f"{card_type.upper()}\n")
            for front, back in cards.items():
                txt.write(f"{front} // {back}\n")
            txt.write("\n")
    print("[write] complete")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download multifaced MTG cards from Scryfall."
    )
    parser.add_argument(
        "--types",
        nargs="+",
        default=DEFAULT_TYPES,
        help=(
            "Card face types to query from Scryfall "
            "(default: split transform dfc mdfc adventure)."
        ),
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output text filename (default: auxiliary/MULTIFACED_CARDS.txt).",
    )
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    print(f"[init] types={args.types}")
    cards_by_type = fetch_multifaced_cards(args.types)

    for card_type, cards in cards_by_type.items():
        print(f"{card_type}: {len(cards)}")

    write_output(args.output, cards_by_type)
    print(f"Wrote output to: {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())