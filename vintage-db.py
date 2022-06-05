import mysql.connector
import pandas as pd
from datetime import datetime
from datetime import date
import calendar
import requests
import warnings
warnings.filterwarnings('ignore')

def get_login():
	with open("mysql.txt") as f:
		lines = f.read().split("\n")
		for i in lines:
			if i.split("=")[0] == "host":
				host = i.split("=")[1]
			if i.split("=")[0] == "user":
				user = i.split("=")[1]
			if i.split("=")[0] == "passwd":
				passwd = i.split("=")[1]
	print("Getting MySQL Login.")
	return (host, user, passwd)
def get_sheet(spreadsheetID, sheetID, create_date):
	url = f"https://docs.google.com/spreadsheets/d/{spreadsheetID}/gviz/tq?tqx=out:csv&gid={sheetID}"
	res = requests.get(url)
	with open(f"vintage-metagame-rawdata-{create_date}.csv", "wb") as f:
	    f.write(res.content)
	print(f"Saved latest metagame data: vintage-metagame-rawdata-{create_date}.csv")
def clean_merged_data(create_date):
	vintage = pd.read_csv(f"vintage-metagame-rawdata-{create_date}.csv", 
						  names=["rank","player","wins","losses","byes","arch","subarch","deck","details","date","event_type"],
						  skiprows = 1,
						  usecols = [i for i in range(11)])
	
	# Replace NA values in 'byes' column with 0.
	vintage.byes = vintage.byes.fillna(0)
	vintage.byes = vintage.byes.astype("int")

	# Propagate 'event_type' data to each record.
	vintage["event_type"].replace({"Showcase Qualifier": "Showcase_Qualifier"}, inplace=True)

	event_type = vintage.event_type.tolist()
	for index,i in enumerate(event_type):
	    if isinstance(i, str):
	        new = i
	    else:
	        event_type[index] = new
	vintage["event_type"] = event_type

	# Create unique 'event_id' column. Format event_date string.
	event_id = []
	dates = vintage.date.tolist()
	event_type = vintage.event_type.to_list()
	dates_new = []
	for index,i in enumerate(dates):
		month = i.split("/")[0].zfill(2)
		day = i.split("/")[1].zfill(2)
		year = i.split("/")[2]
		event_id.append(f"20{year}-{month}-{day}-{event_type[index]}")
		dates_new.append(f"20{year}-{month}-{day}")
	vintage["event_id"] = event_id

	# Create a second table called Events. Remove duplicate records such that each row represents a unique event.
	events = pd.DataFrame({"event_id" : event_id, "event_type" : event_type, "date" : dates_new})
	events = events.groupby(["event_id"], as_index=False)["event_type", "date"].last()

	# Add 'entries' column to Events table to represents number of players in each event.
	players = vintage.groupby(["event_id"], as_index=False)["rank"].max()

	events = events.merge(players, on="event_id")
	events.rename(columns={"rank" : "entries", "date" : "event_date"}, inplace=True)

	# Add 'day_of_week' column to Events table.
	events["day_of_week"] = events["event_date"].apply(lambda x: calendar.day_name[datetime.strptime(x, "%Y-%m-%d").weekday()])


	# Drop 'details' column. Drop 'date' and 'event_type' columns that are now in the Events table.
	vintage.drop(["details"], axis=1, inplace=True)
	vintage.drop(["date"], axis=1, inplace=True)
	vintage.drop(["event_type"], axis=1, inplace=True)

	# Rename 'rank' column to 'finish'.
	vintage.rename(columns={"rank" : "finish"}, inplace=True)

	# Replace commas because it breaks CSV importing with MySQL.
	vintage["arch"] = vintage["arch"].apply(lambda x: str(x).replace(",", ""))
	vintage["subarch"] = vintage["subarch"].apply(lambda x: str(x).replace(",", ""))
	vintage["deck"] = vintage["deck"].apply(lambda x: str(x).replace(",", ""))

	# Save and export to CSV.
	vintage.to_csv(f"vintage-results-{create_date}.csv", index=False)
	events.to_csv(f"vintage-events-{create_date}.csv", index=False)

	print(f"Saved cleaned data: vintage-results-{create_date}.csv, vintage-events-{create_date}.csv")

create_date = date.today().strftime("%Y-%m-%d")
get_sheet("1wxR3iYna86qrdViwHjUPzHuw6bCNeMLb72M25hpUHYk", "1693401931", create_date)
clean_merged_data(create_date)

host, user, passwd = get_login()

vintage_db = mysql.connector.connect(
	host = host,
	user = user,
	passwd = passwd,
	allow_local_infile = True
)
cursor = vintage_db.cursor()

load_events_sql = """
	LOAD DATA LOCAL INFILE %s
	INTO TABLE vintage_metagame_db.vintage_events
	FIELDS TERMINATED BY ","
	OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY '\r\n'
	IGNORE 1 ROWS;
"""

load_results_sql = """
	LOAD DATA LOCAL INFILE %s
	INTO TABLE vintage_metagame_db.vintage_results
	FIELDS TERMINATED BY ","
	OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY '\r\n'
	IGNORE 1 ROWS;
"""

events_fn = (f"vintage-events-{create_date}.csv",)
results_fn = (f"vintage-results-{create_date}.csv",)

cursor.execute(load_events_sql, events_fn)
print("Executed 'load_events' SQL statement.")
cursor.execute(load_results_sql, results_fn)
print("Executed 'load_results' SQL statement.")

vintage_db.commit()
print("Committed changes.")