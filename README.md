## espn-ff-scores.py
    - Download weekly scores and matchups from ESPN Fantasy Football leagues and save to .csv.
    - Login will be prompted for if league is not set to public.
    - Approximate run time: 2 minutes/year.
    - Required Inputs: League ID, Year, and Total Scoring Periods (Regular Season Weeks + Post-season Rounds).
## mtg-goldfish-lists.py
    - Scrapes MTGGoldfish.com for uniquely named decklists with 2 or more occurrences.
    - Saves lists as .txt files separated into folders by Month, then further saves an ALL_DECKS file for use with MTGO-Tracker.
    - Required Inputs: Month (YYYY-MM), Format.
## pgn-script.py
    - Parses all .pgn files in script folder location.
    - Creates a table with each record representing individual chess moves and resulting board state.
    - Saves table as .csv file.
    - Required Inputs: Folder containing one or more .pgn files and script file.
## sportradar-nfl.py
    - Used to interact with Sportradar NFL API.
    - Download Season, Season Schedule, Game_IDs, and Play-By-Play data.
    - Parses Play-By-Play .json data and writes to .csv.
    - Require Inputs: Sportradar API key.
