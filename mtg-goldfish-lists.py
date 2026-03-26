import argparse
import requests
import os
import time
import sys
from bs4 import BeautifulSoup
import pickle
import io
import zipfile
import shutil
import re
import itertools
from pathlib import Path
from datetime import datetime

count = 0
short_list = []
all_decks = []
ad = {}

def format_deckname(name):
    # Input:  String
    # Output: String
    name_formatted = name

    def replace_color_permutations(text, letters, replacement):
        # Match all orderings with optional dashes between letters.
        for perm in itertools.permutations(letters, len(letters)):
            token = r"(?:\s*-\s*)?".join(perm)
            pattern = rf"(?<![A-Za-z]){token}(?![A-Za-z])"
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    # 5-color (all permutations, case-insensitive, optional dashes)
    name_formatted = replace_color_permutations(name_formatted, ("W", "U", "B", "R", "G"), "5c")

    # 4-color (all 5P4 permutations = 120 variants)
    for four_colors in itertools.combinations(("W", "U", "B", "R", "G"), 4):
        name_formatted = replace_color_permutations(name_formatted, four_colors, "4c")

    # 3-color shards/wedges (all permutations for each color set)
    tri_color_map = {
        ("W", "U", "G"): "Bant",
        ("W", "U", "B"): "Esper",
        ("U", "B", "R"): "Grixis",
        ("B", "R", "G"): "Jund",
        ("R", "G", "W"): "Naya",
        ("W", "B", "G"): "Abzan",
        ("U", "R", "W"): "Jeskai",
        ("B", "U", "G"): "BUG",
        ("W", "B", "R"): "Mardu",
        ("R", "G", "U"): "RUG",
    }
    for tri_colors, replacement in tri_color_map.items():
        name_formatted = replace_color_permutations(name_formatted, tri_colors, replacement)

    # Common named aliases
    name_formatted = re.sub(r"\bSultai\b", "BUG", name_formatted, flags=re.IGNORECASE)
    name_formatted = re.sub(r"\bTemur\b", "RUG", name_formatted, flags=re.IGNORECASE)

    # 2-color guild names and abbreviations
    dual_color_map = {
        ("W", "U"): "UW",
        ("W", "R"): "RW",
        ("B", "U"): "UB",
        ("B", "G"): "GB",
        ("G", "R"): "RG",
        ("R", "U"): "UR",
        ("W", "B"): "BW",
        ("B", "R"): "RB",
        ("W", "G"): "GW",
        ("G", "U"): "UG",
    }
    for dual_colors, replacement in dual_color_map.items():
        name_formatted = replace_color_permutations(name_formatted, dual_colors, replacement)

    guild_word_map = {
        "Azorius": "UW",
        "Dimir": "UB",
        "Golgari": "GB",
        "Gruul": "RG",
        "Izzet": "UR",
        "Orzhov": "BW",
        "Rakdos": "RB",
        "Selesnya": "GW",
        "Simic": "UG",
    }
    for guild_name, replacement in guild_word_map.items():
        name_formatted = re.sub(rf"\b{guild_name}\b", replacement, name_formatted, flags=re.IGNORECASE)

    # Mono color name patterns
    mono_color_map = {
        "white": "W",
        "blue": "U",
        "black": "B",
        "red": "R",
        "green": "G",
    }
    for color_name, replacement in mono_color_map.items():
        mono_pattern = rf"\bmono(?:\s*-\s*|\s*){color_name}\b|\bmono(?:\s*-\s*|\s*){replacement}\b"
        name_formatted = re.sub(mono_pattern, replacement, name_formatted, flags=re.IGNORECASE)

    # Additional color-count aliases
    name_formatted = name_formatted.replace("'", "")
    name_formatted = re.sub(r"\b(?:five(?:\s*-\s*)?color(?:ed|s)?|5(?:\s*-\s*)?color)\b", "5c", name_formatted, flags=re.IGNORECASE)
    name_formatted = re.sub(r"\b(?:four(?:\s*-\s*)?color(?:ed|s)?|4(?:\s*-\s*)?color)\b", "4c", name_formatted, flags=re.IGNORECASE)

    return name_formatted
def get_dates(yyyy_mm):
    date1 = yyyy_mm[0:4] + "-" + yyyy_mm[5:7] + "-" + "01"
    date2 = yyyy_mm[0:4] + "-" + yyyy_mm[5:7] + "-"
    if yyyy_mm[5:7] == "01":
        return [date1,date2+"31"]
    if yyyy_mm[5:7] == "02":
        return [date1,date2+"28"]
    if yyyy_mm[5:7] == "03":
        return [date1,date2+"31"]
    if yyyy_mm[5:7] == "04":
        return [date1,date2+"30"]
    if yyyy_mm[5:7] == "05":
        return [date1,date2+"31"]
    if yyyy_mm[5:7] == "06":
        return [date1,date2+"30"]
    if yyyy_mm[5:7] == "07":
        return [date1,date2+"31"]
    if yyyy_mm[5:7] == "08":
        return [date1,date2+"31"]
    if yyyy_mm[5:7] == "09":
        return [date1,date2+"30"]
    if yyyy_mm[5:7] == "10":
        return [date1,date2+"31"]       
    if yyyy_mm[5:7] == "11":
        return [date1,date2+"30"]
    if yyyy_mm[5:7] == "12":
        return [date1,date2+"31"]
def get_search_url(format,yyyy_mm):
    # Date: YYYY-MM-DD

    date1 = get_dates(yyyy_mm)[0]
    date2 = get_dates(yyyy_mm)[1]

    url = "https://www.mtggoldfish.com/tournament_searches/create?utf8=%E2%9C%93&tournament_search%5Bname%5D=&tournament_search%5Bformat%5D="
    url += format.lower()
    url += "&tournament_search%5Bdate_range%5D="
    url += date1[5:7] + "%2F" + date1[8:10] + "%2F" + date1[0:4] + "+-+"
    url += date2[5:7] + "%2F" + date2[8:10] + "%2F" + date2[0:4] + "&commit=Search"
    print(url)
    return url
def get_tournaments(search_url):
    # MTGGoldfish tournament searches are paginated. Read every page so we don't
    # only scrape the most recent few days of a month.
    t_list = []
    page_num = 1
    while True:
        page_url = search_url if page_num == 1 else f"{search_url}&page={page_num}"
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, "html.parser")

        # Find tournament search result table
        table = soup.find("table", class_="table table-striped")
        if table is None:
            break

        # Each row in the table is a tournament
        tourneys = table.find_all("tr")
        rows_added = 0
        for i in tourneys:
            # Each element represents information about the tournament
            # [Date, Name, Format]
            elements = i.find_all("td")
            if len(elements) < 1:
                continue

            # Links represents all links found in this row (there is only one link)
            # Link => URL of tournament page
            links = i.find_all("a")
            link = "http://www.mtggoldfish.com"
            for j in links:
                link += j["href"]

            # Attributes represents descriptive details about the tournament
            # List of strings
            # [Date, Name, Format]
            attributes = []
            for j in elements:
                attributes.append(j.text.strip())

            attributes.append(link)
            t_list.append(attributes)
            rows_added += 1

        # No table rows on this page means pagination ended.
        if rows_added == 0:
            break
        page_num += 1
    return t_list
def get_decks(tourney):
    print(tourney)
    t_format = tourney[2]
    tourney_url = tourney[-1]
    page = requests.get(tourney_url)

    # Get entire site in HTML
    soup = BeautifulSoup(page.content,"html.parser")

    decks = soup.find_all("tr",class_="tournament-decklist-event") + soup.find_all("tr",class_="tournament-decklist-odd")

    link = "http://www.mtggoldfish.com/deck/download/"
    d_list = []
    for i in decks:
        elements = i.find_all("td")
        links = i.find_all("a")
        name = elements[1].text.replace(" \u2744"," Snow")
        name = name.replace("\u2744"," Snow")
        name = name.replace("/","")
        if ("(" in name) and (")" in name):
            name = name.split("(")[0] + name.split(")")[1]
        name = name.strip()

        attributes = []
        attributes.append(name)
        attributes.append(t_format)
        attributes.append(link + links[0]["href"].split("/deck/")[1])
        attributes.append(1)

        d_list.append(attributes)

    return d_list
def get_decklist(deck):
    name = deck[0]
    d_format = deck[1]
    deck_url = deck[2]

    for attempt in range(1, THROTTLE_MAX_RETRIES + 1):
        page = requests.get(deck_url, timeout=30)
        deck_list = page.text.replace("\r","")

        if "Throttled" in deck_list:
            if attempt < THROTTLE_MAX_RETRIES:
                print(f"Throttled fetching decklist: {name} ({d_format}). Retrying in {THROTTLE_RETRY_WAIT}s...")
                time.sleep(THROTTLE_RETRY_WAIT)
                continue
            print(f"Throttled after {THROTTLE_MAX_RETRIES} attempts, skipping: {name} ({d_format})")
            return None

        return [name,d_format,deck_list]

    return None
def save_decklist(decklist,yyyy_mm):
    global count
    global short_list

    name = decklist[0]
    dl_format = decklist[1]
    dl_string = decklist[2]

    month_dir = LISTS_DIR / yyyy_mm
    month_dir.mkdir(parents=True, exist_ok=True)
    file_name = sanitize_windows_filename(dl_format + " - " + name + ".txt")
    with open(month_dir / file_name,"w", encoding="utf-8") as txt:
        txt.write(dl_string)

    if len(dl_string) < 150:
        short_list.append(dl_format + " - " + name)
        count += 1
def save_receipt(yyyy_mm):
    print("number of short lists: " + str(len(short_list)))
    print("number of total lists: " + str(len(all_decks)))
    file_name = yyyy_mm + ".txt"
    LISTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(LISTS_DIR / file_name,"w",encoding="utf-8") as txt:
        txt.write("number of short lists: " + str(len(short_list)))
        txt.write("\n")
        txt.write("number of total lists: " + str(len(all_decks)))
        txt.write("\n")
        txt.write("------------")
        txt.write("\n")
        for i in short_list:
            txt.write(i)
            txt.write("\n")
        txt.write("------------")
        txt.write("\n")
        for i in all_decks:
            #print(i)
            txt.write("['"+i[0]+"', '"+i[1]+"', '"+i[2]+"', "+str(i[3])+"]")
            txt.write("\n")
        txt.write("------------")
def save_all_lists(d_format,yyyy_mm):
    global all_decks
    global short_list
    short_list = []

    url = get_search_url(d_format,yyyy_mm)

    # Tourneys represents list of Tournament objects
    # [Date, Name, Format, URL]
    tourneys = get_tournaments(url)

    # Decks represents list of Deck objects
    # [Name, Format, URL, Count]
    # Get all deck objects from our list of Tournaments
    decks = []
    decks_filtered = []
    deck_set = set()
    for tourney in tourneys:
        new_decks = get_decks(tourney)
        for i in new_decks:
            if (i[0] in deck_set):
                for j in decks:
                    if j[0] == i[0]:
                        j[3] += 1
                        break
            else:
                deck_set.add(i[0])
                decks.append(i)

    for i in decks:
        if i[3] > 1:
            decks_filtered.append(i)
    
    # Decklists represents list of Decklist objects
    # [Name, Format, DecklistString]
    # Get all Decklist objects from our list of Decks
    decklists = []
    throttled_skips = 0
    for i in decks_filtered:
        decklist = get_decklist(i)
        if decklist is None:
            throttled_skips += 1
            continue
        decklists.append(decklist)

    # For each Decklist object found, save the Decklist as a .txt file
    for i in decklists:
        save_decklist(i,yyyy_mm)

    all_decks += decks_filtered
    print(
        d_format
        + " done. "
        + str(len(decklists))
        + " decklists saved."
        + (f" ({throttled_skips} skipped due to throttling)." if throttled_skips else "")
    )
def save_multiple_months(months,formats):
    global all_decks
    for yyyy_mm in months:
        all_decks = []
        print("starting month: " + yyyy_mm)
        for fmt in formats:
            save_all_lists(fmt,yyyy_mm)
            if (yyyy_mm == months[-1]) and (fmt == formats[-1]):
                pass
            else:
                time.sleep(wait_time)
        print(yyyy_mm + " done.")
        #save_receipt(yyyy_mm)
def parse_list(filename,init):
    # Input:  String,String
    # Output: [String,String,Set{MaindeckCards}]

    initial = init.split("\n")
    maindeck = []
    sideboard = []
    card_count = 0
    card = ""
    sb = False
    
    if initial[-1] == "":
        initial.pop()
    
    for i in initial:
        if i == "" and sb == False:
            sb = True
        else:
            try:
                card_count = int(i.split(" ",1)[0])
            except ValueError:
                return None
            card = i.split(" ",1)[1]
            while card_count > 0 and sb == False:
                maindeck.append(card)
                card_count -= 1
            while card_count > 0 and sb == True:
                sideboard.append(card)
                card_count -= 1
    
    # Customize Deck Naming Conventions
    d_format = filename.split(".txt")[0].split(" - ")[0].strip()
    name = filename.split(".txt")[0].split(" - ")[1].strip()
    
    old = name
    name = format_deckname(name).strip()
    # if ("Mono" in old) or ("mono" in old):
    #     print(name)

    return [name, d_format, set(maindeck)]
def get_lists(all_decks_output_path=None):
    global ad
    errors = []
    dedupe_counts_by_month_format = {}
    total_duplicates_skipped = 0

    LISTS_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(LISTS_ZIP_PATH, mode='w') as zf:
        folders = [p for p in LISTS_DIR.iterdir() if p.is_dir()]
        for month_path in folders:
            i = month_path.name
            month_key = str(i).strip()
            if i == 'Lists.zip':
                continue
            # print("Parsing Month: " + i)
            files = [p for p in month_path.iterdir() if p.is_file()]
            month_decks = []
            seen_keys = set()
            for file_path in files:
                j = file_path.name
                zf.write(file_path, (i + '\\' + j))
                with io.open(file_path,"r",encoding="ansi") as decklist:
                    initial = decklist.read()
                deck = parse_list(j,initial)
                if deck == None:
                    errors.append((i,j))
                    continue

                deck_nm = str(deck[0]).strip()
                format_nm = str(deck[1]).strip()
                deck_lst = deck[2]
                normalized_deck = [deck_nm, format_nm, deck_lst]
                key = (month_key, deck_nm, format_nm)
                if key in seen_keys:
                    month_fmt = (month_key, format_nm)
                    dedupe_counts_by_month_format[month_fmt] = dedupe_counts_by_month_format.get(month_fmt, 0) + 1
                    total_duplicates_skipped += 1
                    continue
                seen_keys.add(key)
                month_decks.append(normalized_deck)

            ad[month_key] = month_decks

    print(f"Imported Sample Decklists. {len(errors)} error(s) found.")
    error_counts_by_month_format = {}
    for yyyy_mm, filename in errors:
        if " - " in filename:
            format_nm = filename.split(" - ", 1)[0]
        else:
            format_nm = "UNKNOWN"
        key = (yyyy_mm, format_nm)
        error_counts_by_month_format[key] = error_counts_by_month_format.get(key, 0) + 1

    print("Error counts by YYYY-MM / format_nm:")
    if not error_counts_by_month_format:
        print("  (none)")
    else:
        for yyyy_mm, format_nm in sorted(error_counts_by_month_format):
            count = error_counts_by_month_format[(yyyy_mm, format_nm)]
            print(f"  {yyyy_mm} / {format_nm}: {count}")

    print("Deduped duplicates by YYYY-MM / format_nm:")
    if not dedupe_counts_by_month_format:
        print("  (none)")
    else:
        for yyyy_mm, format_nm in sorted(dedupe_counts_by_month_format):
            count = dedupe_counts_by_month_format[(yyyy_mm, format_nm)]
            # print(f"  {yyyy_mm} / {format_nm}: {count}")
    print(f"Total duplicates skipped: {total_duplicates_skipped}")

    if all_decks_output_path is None:
        all_decks_output_path = DEFAULT_ALL_DECKS_OUTPUT
    output_path = Path(all_decks_output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as output_file:
        pickle.dump(ad, output_file)
    print(f"Wrote ALL_DECKS to: {output_path}")
    print(f"Wrote Lists.zip to: {LISTS_ZIP_PATH}")

# Wait time between format scrapes (seconds). Prevents throttling.
wait_time = 120
THROTTLE_RETRY_WAIT = 15
THROTTLE_MAX_RETRIES = 20

DEFAULT_FORMATS = ["legacy","modern","pauper","pioneer","premodern","standard","vintage"]
DEFAULT_ALL_DECKS_OUTPUT = str(Path(__file__).resolve().parent / "auxiliary" / "ALL_DECKS")
AUXILIARY_DIR = Path(__file__).resolve().parent / "auxiliary"
LISTS_DIR = AUXILIARY_DIR / "lists"
LISTS_ZIP_PATH = AUXILIARY_DIR / "Lists.zip"
LOGS_DIR = AUXILIARY_DIR / "logs"
INVALID_FILENAME_CHARS = '<>:"/\\|?*'

class TeeStream:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()

def setup_log_output(log_output_path=None):
    if log_output_path is None:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_output_path = LOGS_DIR / f"mtg-goldfish-lists-{stamp}.log"
    else:
        log_output_path = Path(log_output_path)
        log_output_path.parent.mkdir(parents=True, exist_ok=True)

    log_file = open(log_output_path, "w", encoding="utf-8", buffering=1)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = TeeStream(original_stdout, log_file)
    sys.stderr = TeeStream(original_stderr, log_file)
    return log_file, original_stdout, original_stderr, Path(log_output_path)


def sanitize_windows_filename(filename: str) -> str:
    cleaned = filename
    for ch in INVALID_FILENAME_CHARS:
        cleaned = cleaned.replace(ch, "-")
    cleaned = cleaned.rstrip(" .")
    return cleaned or "unnamed"

def _validate_month(month_value):
    if re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month_value) is None:
        raise argparse.ArgumentTypeError(
            f"Invalid month '{month_value}'. Expected format YYYY-MM."
        )
    return month_value

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Download MTGGoldfish decklists and build ALL_DECKS pickle. "
            "Months may be provided in YYYY-MM format to refresh list files."
        )
    )
    parser.add_argument(
        "--months",
        nargs="+",
        required=False,
        default=None,
        type=_validate_month,
        help='Optional list of months, e.g. --months 2026-01 2026-02',
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=DEFAULT_FORMATS,
        help=(
            "Optional list of formats. "
            "Default: legacy modern pauper pioneer premodern standard vintage"
        ),
    )
    parser.add_argument(
        "--all-decks-output",
        default=DEFAULT_ALL_DECKS_OUTPUT,
        help="Output path for ALL_DECKS pickle (default: auxiliary/ALL_DECKS).",
    )
    parser.add_argument(
        "--log-output",
        default=None,
        help="Optional log file path. Default: auxiliary/logs/mtg-goldfish-lists-YYYYMMDD-HHMMSS.log",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    log_file, original_stdout, original_stderr, log_path = setup_log_output(args.log_output)
    print(f"Logging to: {log_path}")
    try:
        if args.months:
            save_multiple_months(args.months, args.formats)
        else:
            print("No --months provided; skipping save_multiple_months().")
        get_lists(args.all_decks_output)
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()

if __name__ == "__main__":
    main()