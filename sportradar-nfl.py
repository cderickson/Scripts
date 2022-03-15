import http.client
import time
import os
import io
import json
import pandas as pd
import csv

def get_api_keys():
	KEYS = {}
	with io.open("sportradar_keys.txt","r",encoding="ansi") as file:
		initial = file.read().split("\n")
		for i in initial:
			KEYS[i.split()[0]] = i.split()[2]
	return KEYS

def get_seasons():
	# Seasons
	# List of all available seasons (including pre/post-seasons)
	# {
	# league  : {id, name, alias}
	# seasons : [{id, year, start_date, end_date, status, type}]
	# }

	conn = http.client.HTTPSConnection("api.sportradar.us")
	conn.request("GET", "/nfl/official/trial/v7/en/league/seasons.json?api_key=" + KEYS["NFL_KEY"])
	res = conn.getresponse()
	data = res.read()
	return json.loads(data.decode("utf-8"))

def get_pbp(GAME_ID):
	# Play-By-Play

	conn = http.client.HTTPSConnection("api.sportradar.us")
	conn.request("GET", f"/nfl/official/trial/v7/en/games/{GAME_ID}/pbp.json?api_key=" + KEYS["NFL_KEY"])
	res = conn.getresponse()
	data = res.read()
	return json.loads(data.decode("utf-8"))

def get_season_schedule(YEAR,SEASON_TYPE):
	# Season Schedule
	# {
	# id, year, type, name, weeks : [{id, sequence, title, games : [{id, status, scheduled, attendance, ...}]}]
	# }

	conn = http.client.HTTPSConnection("api.sportradar.us")
	conn.request("GET", f"/nfl/official/trial/v7/en/games/{YEAR}/{SEASON_TYPE}/schedule.json?api_key=" + KEYS["NFL_KEY"])
	res = conn.getresponse()
	data = res.read()
	return json.loads(data.decode("utf-8"))

def get_game_id_list(SEASON_SCHEDULE):
	# Input: Season Schedule in JSON
	# Output: List[Game_IDs]

	game_id_list = []
	for week in SEASON_SCHEDULE["weeks"]:
		for game in week["games"]:
			game_id_list.append(game["id"])
	return game_id_list

def save_pbp(YEAR, SEASON_TYPE):
	season_schedule = get_season_schedule(YEAR,SEASON_TYPE)
	game_id_list = get_game_id_list(season_schedule)
	print(f"Game_IDs Found: {len(game_id_list)}")

	root = os.getcwd()
	if os.path.isdir(str(YEAR) + "-Games") == False:
		os.mkdir(str(YEAR) + "-Games")
	os.chdir(root + "\\" + str(YEAR) + "-Games")

	for i in game_id_list:
		print(f"Retrieving Play-By-Play: {i}.json")
		pbp = get_pbp(i)
		with open(f"{i}.json", "w") as file:
			file.write(json.dumps(pbp, indent = 4))
		time.sleep(15)
	os.chdir(root)

def parse_play(GAME,play,count):
	curr_play = []
	if "event_type" in play:
		return []
	else:
		if ("deleted" in play):
			if play["deleted"] == True:
				return []
		elif play["play_type"] == "penalty":
			return []
		else:
			if ("PENALTY" in play["description"]) and ("No Play." in play["description"]):
				accepted_penalty = False
				for i in play["details"]:
					if i["category"] == "penalty":
						if i["penalty"]["result"] != "declined":
							accepted_penalty = True
				if accepted_penalty == True:
					return []
			curr_play.extend([count])
			curr_play.extend([GAME["id"]])
			curr_play.extend([GAME["summary"]["home"]["alias"]])
			curr_play.extend([GAME["summary"]["away"]["alias"]])
			curr_play.extend([GAME["summary"]["season"]["year"]])
			curr_play.extend([GAME["summary"]["week"]["title"]])
			curr_play.extend([play["clock"]])
			curr_play.extend([play["description"]])
			curr_play.extend([play["fake_field_goal"]])
			curr_play.extend([play["fake_punt"]])
			try:
				curr_play.extend([play["hash_mark"]])
			except KeyError:
				curr_play.extend(["NA"])
			curr_play.extend([play["play_action"]])
			curr_play.extend([play["run_pass_option"]])
			curr_play.extend([play["screen_pass"]])

			if (play["play_type"] == "rush") or (play["play_type"] == "pass"):
				if "PENALTY" in play["description"]:
					curr_play.extend(["NA","NA","NA","NA","NA","NA","NA","NA"])
				else:
					curr_play.extend([play["blitz"]])
					curr_play.extend([play["huddle"]])
					curr_play.extend([play["left_tightends"]])
					try:
						curr_play.extend([play["men_in_box"]])
					except KeyError:
						curr_play.extend(["NA"])
					try:
						curr_play.extend([play["play_direction"]])
					except:
						curr_play.extend(["NA"])
					curr_play.extend([play["qb_at_snap"]])
					curr_play.extend([play["right_tightends"]])
					try:
						curr_play.extend([play["running_lane"]])
					except KeyError:
						curr_play.extend(["NA"])
			else:
				curr_play.extend(["NA","NA","NA","NA","NA","NA","NA","NA"])

			if (play["play_type"] == "pass"):
				if "PENALTY" in play["description"]:
					curr_play.extend(["NA","NA","NA"])
				else:
					try:
						curr_play.extend([play["pass_route"]])
					except KeyError:
						curr_play.extend(["NA"])
					try:
						curr_play.extend([play["players_rushed"]])
					except KeyError:
						curr_play.extend(["NA"])
					try:
						curr_play.extend([play["pocket_location"]])
					except KeyError:
						curr_play.extend(["NA"])
			else:
				curr_play.extend(["NA","NA","NA"])
			
			pass_stat = False
			rec_stat = False
			rush_stat = False
			kick_stat = False
			no_play = False
			for i in play["details"]:
				if i["category"] == "no_play":
					no_play = True
					curr_play.extend(["NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA"])
					break

			if no_play == False:
				for i in play["statistics"]:
					#print(i["stat_type"])
					if i["stat_type"] == "pass":
						pass_stat = True
					elif i["stat_type"] == "receive":
						rec_stat = True
					elif i["stat_type"] == "rush":
						rush_stat = True
					elif i["stat_type"] == "kick":
						kick_stat = True

				if pass_stat == False:
					curr_play.extend(["NA","NA","NA","NA"])
				else:
					for i in play["statistics"]:
						if i["stat_type"] == "pass":
							curr_play.extend([i["hurry"]])
							curr_play.extend([i["knockdown"]])
							curr_play.extend([i["on_target_throw"]])
							try:
								curr_play.extend([i["pocket_time"]])
							except KeyError:
								curr_play.extend(["NA"])
							break
				if rec_stat == False:
					curr_play.extend(["NA","NA","NA"])
				else:
					for i in play["statistics"]:
						if i["stat_type"] == "receive":
							curr_play.extend([i["catchable"]])
							try:
								curr_play.extend([i["dropped"]])
							except:
								curr_play.extend(["NA"])
							try:
								curr_play.extend([i["yards_after_contact"]])
							except KeyError:
								curr_play.extend(["NA"])
							break
				if rush_stat == False:
					curr_play.extend(["NA","NA"])
				else:
					for i in play["statistics"]:
						if i["stat_type"] == "rush":
							try:
								curr_play.extend([i["broken_tackles"]])
							except KeyError:
								curr_play.extend(["NA"])
							try:
								curr_play.extend([i["yards_after_contact"]])
							except KeyError:
								curr_play.extend(["NA"])
							break
				if kick_stat == False:
					curr_play.extend(["NA","NA","NA"])
				else:
					for i in play["statistics"]:
						if i["stat_type"] == "kick":
							curr_play.extend([i["onside_attempt"]])
							curr_play.extend([i["onside_success"]])
							curr_play.extend([i["squib_kick"]])
							break
	return curr_play

def fix_play(curr_play):
	if curr_play == []:
		return []

	play = curr_play
	for index,i in enumerate(play):
		if i == False:
			play[index] = 0
		elif i == True:
			play[index] = 1
	if play[2] == "JAC":
		play[2] = "JAX"
	if play[3] == "JAC":
		play[3] = "JAX"
	play[5] = str(play[5]).zfill(2)
	play.insert(0,str(play[4]) + "_" + play[5] + "_" + play[3] + "_" + play[2])
	play[1] = play[0] + "_" + str(play[1])
	return play

def parse(GAME):
	count = 1
	play_list = []
	curr_play = []
	for quarter in GAME["periods"]:
		for event in quarter["pbp"]:
			if ("deleted" in event):
				if event["deleted"] == True:
					continue
			elif event["type"] == "event":
				# Non-drive found.
				continue
			elif event["type"] == "play":
				curr_play = parse_play(GAME,event,count)
				curr_play = fix_play(curr_play)
				if curr_play != []:
					play_list.append(curr_play)
					count += 1
				if (len(curr_play) != 38) & (len(curr_play) > 0):
					print(GAME["id"] + "::::" + play["id"])
				curr_play = []
			elif event["type"] == "drive":
				# Drive found.
				for play in event["events"]:
					curr_play = parse_play(GAME,play,count)
					curr_play = fix_play(curr_play)
					if curr_play != []:
						play_list.append(curr_play)
						count += 1
					if (len(curr_play) != 38) & (len(curr_play) > 0):
						print(GAME["id"] + "::::" + play["id"] + "::::" + str(len(curr_play)))
					curr_play = []
	return play_list

def parse_folder(YEAR):
	root = os.getcwd()
	os.chdir(root + "\\" + str(YEAR))

	play_list = []
	files = os.listdir()
	for file in files:
		#print(file)
		with io.open(file) as data:
			pbp = json.load(data)
		pbp_parsed = parse(pbp)
		play_list.extend(pbp_parsed)
	os.chdir(root)
	print(len(play_list))
	return play_list

def headers():
	return ["NEW_GAME_ID",
			"UNIQUE_PLAY_ID",
			"SPORTRADAR_GAME_ID",
			"HOME_TEAM_ABBR",
			"AWAY_TEAM_ABBR",
			"SEASON_NUM",
			"WEEK_NUM",
			"CLOCK",
			"DESCRIPTION",
			"FAKE_FG",
			"FAKE_PUNT",
			"HASH_MARK",
			"PLAY_ACTION",
			"RPO",
			"SCREEN_PASS",
			"BLITZ",
			"HUDDLE",
			"LEFT_TIGHTENDS",
			"MEN_IN_BOX",
			"PLAY_DIRECTION",
			"QB_AT_SNAP",
			"RIGHT_TIGHTENDS",
			"RUNNING_LANE",
			"PASS_ROUTE",
			"PLAYERS_RUSHED",
			"POCKET_LOCATION",
			"HURRY",
			"KNOCKDOWN",
			"ON_TARGET_THROW",
			"POCKET_TIME",
			"CATCHABLE",
			"DROPPED",
			"YARDS_AFTER_CONTACT_REC",
			"BROKEN_TACKLES_RUSH",
			"YARDS_AFTER_CONTACT_RUSH",
			"ONSIDE_ATTEMPT",
			"ONSIDE_SUCCESS",
			"SQUIB"]

def write_plays_to_csv(DATA):
	with open("2021-Sportradar-NFL.csv","w",encoding="UTF8",newline="") as file:
		df_rows = pd.DataFrame(DATA, columns=headers()).to_numpy().tolist()
		writer = csv.writer(file)
		writer.writerow(headers())
		for row in df_rows:
			writer.writerow(row)

KEYS = get_api_keys()

# save_pbp("2021","reg")

data = parse_folder(2021)
write_plays_to_csv(data)
