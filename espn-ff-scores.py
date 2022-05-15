import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

def replace_names(weekly_scores_dict):
	# Populate 'name_dict' with team/player name pairs if you want team nicknames to be replaced with the name of the manager.
	# ESPN saves team names at end of year.
	name_dict = {
		"TEAM_NAME_HERE" : "PLAYER_NAME_HERE"
	}

	key_list = list(weekly_scores_dict.keys())
	for i in key_list:
		if i in name_dict:
			weekly_scores_dict[name_dict[i]] = weekly_scores_dict.pop(i)
	for i in weekly_scores_dict:
		if weekly_scores_dict[i]["opp"] in name_dict:
			weekly_scores_dict[i]["opp"] = name_dict[weekly_scores_dict[i]["opp"]]
	return weekly_scores_dict
def get_week_urls(league_id,year_length,year_num):
	weeks = list(range(1, year_length + 1))
	url_dict = {}
	for i in weeks:
		url = "https://fantasy.espn.com/football/league/scoreboard?seasonId="
		url += year_num
		url += "&leagueId="
		url += league_id
		url += "&matchupPeriodId="
		url += str(i)
		url += "&mSPID=1"
		url_dict[str(i)] = url
	return url_dict
def get_scores(url_dict):
	scores_dict = {}
	weekly_scores_dict = {}

	driver = webdriver.Edge()

	first_url = url_dict[list(url_dict.keys())[0]]
	driver.get(first_url)
	time.sleep(45)

	for i in url_dict:
		driver.get(url_dict[i])
		time.sleep(5)

		teams = driver.find_elements(By.CLASS_NAME, "ScoreCell__TeamName")
		scores = driver.find_elements(By.CLASS_NAME, "ScoreCell__Score")

		for index,j in enumerate(teams):
			if (index % 2) == 0:
				opp_index = index + 1
			else:
				opp_index = index - 1
				continue # Remove continue statement to build an inverse joined dataset.
			weekly_scores_dict[j.text] = {"score" : scores[index].text, "opp" : teams[opp_index].text, "opp_score" : scores[opp_index].text}
		weekly_scores_dict = replace_names(weekly_scores_dict)
		scores_dict[i] = weekly_scores_dict
		weekly_scores_dict = {}
	return scores_dict
def to_record_list(score_dict):
	records = []
	for i in score_dict:
		YEAR = i
		for j in score_dict[i]:
			WEEK = j
			for k in score_dict[i][j]:
				TEAM = k
				TEAM_SCORE = score_dict[i][j][k]["score"]
				OPPONENT = score_dict[i][j][k]["opp"]
				OPP_SCORE = score_dict[i][j][k]["opp_score"]
				records.append([YEAR, int(WEEK), TEAM, float(TEAM_SCORE), OPPONENT, float(OPP_SCORE)])
	return records
def export(score_dict,fname):
	df = pd.DataFrame(to_record_list(score_dict), columns = ["year", "week", "team_1", "team_1_score", "team_2", "team_2_score"])
	df.to_csv(fname, index=False)

score_dict = {}

# Inputs
league_id = "39598"
year_num = "2021"
year_length = 15

url_dict = get_week_urls(league_id, year_length, year_num)
score_dict[year_num] = get_scores(url_dict)
export(score_dict, f"ff_scores_{year_num}.csv")
