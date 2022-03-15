## espn-ff-scores.py
Downloads weekly scores and matchups from ESPN Fantasy Football leagues. Required inputs: League ID, Year, and Total Scoring Periods (Regular Season Weeks + Post-season Rounds). Login will be prompted for if league is not set to public. Dataset saved to CSV in tabular format. Approximate run time: ~2 minutes/year.
## mtg-goldfish-lists.py
Scrapes MTGGoldfish.com for uniquely named decklists with 2 or more occurrences by Month (YYYY-MM) and Format. Saves lists as .txt files separated into folders by Month, then further saves an 'ALL_DECKS' file for use with MTGO-Tracker.
## sportradar-nfl.py
Used to interact with Sportradar NFL API. Download Season, Season Schedule, Game_IDs, and Play-By-Play data. Parses Play-By-Play .json data and writes to .csv in tabular format. Requires Sportradar API key.
