import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

def replace_names(weekly_scores_dict):
	name_dict_2014 = {"The Dream Team" : "CHRIS",
					  "Fluffy Bunnybutts" : "CARLEN",
					  "The Legion of Poop" : "ANDREW",
					  "Sir Wallington" : "KYLE",
					  "Darrell Bevell's #1 Fan" : "STEVE",
					  "Sandusky's Daycare" : "DREW",
					  "GB Packers" : "MATT",
					  "Team nationbrickshit" : "NATHAN"}
	name_dict_2015 = {"Season Went ByeByeBye" : "MATT",
					  "Andrew's Best Bud" : "STEVE",
					  "NoSteve for 2015" : "DYLAN",
					  "Legion of Poop" : "ANDREW",
					  "Mayors of Valuetown" : "KYLE",
					  "You Cheater" : "SAM",
					  "I HAVE NO FUTURE" : "NICK",
					  "Team nationbrickshit" : "NATHAN",
					  "Andrew's Black Friend" : "CHRIS",
					  "Fluffy Bunnybutts" : "CARLEN"}
	name_dict_2016 = {"Melvwin Gordon" : "MATT",
					  "MANUAL ENTRY" : "STEVE",
					  "2 POOPY 2 LATE _" : "DYLAN",
					  "The Legion of Poop" : "ANDREW",
					  "Team {|}" : "KYLE",
					  "Chicago Dickholes" : "SAM",
					  "LEAGUE CHAMP" : "NICK",
					  "Team 8---D" : "NATHAN",
					  "Ezekill Myself" : "CHRIS",
					  "Tom Brady youre my only hope" : "CARLEN"}
	name_dict_2017 = {"Gurley Gone Wild" : "MATT",
					  "THE LAST JEDI BEST SW FILM" : "STEVE",
					  "TOP DOG" : "DYLAN",
					  "The Legion of Poop" : "ANDREW",
					  "I love porgs" : "KYLE",
					  "'o o'" : "SAM",
					  "SEE YOU IN 2018 GO JAGS" : "NICK",
					  "XXXXXXXXXXXXXXXXX" : "NATHAN",
					  "g g" : "CHRIS",
					  "OG Fluffy Bunnybutts" : "CARLEN"}
	name_dict_2018 = {"Patrick is Ma Homie" : "MATT",
					  "Juju No Jutsu" : "STEVE",
					  "TOP DOG" : "DYLAN",
					  "The Legion of Shit" : "ANDREW",
					  "2009 New Orleans Aints" : "KYLE",
					  "'o o'" : "SAM",
					  "Sacko Boi" : "NICK",
					  "GiveMeMyGC NoExcuses" : "NATHAN",
					  "2018 Houston Texans" : "CHRIS",
					  "The Brady Bunch" : "CARLEN"}
	name_dict_2019 = {"Patrick is Ma Homie" : "MATT",
					  "EXCITED 4 UR WEDDIN NO JUTSU" : "STEVE",
					  "TOP DOG" : "DYLAN",
					  "The Legion of Minshoop II" : "ANDREW",
					  "Benching All Of My Players" : "KYLE",
					  "'o o'" : "SAM",
					  "Silver Medalist" : "NICK",
					  "StopFuckingKids BeatThemInstead" : "NATHAN",
					  "Cats in Hats" : "CHRIS",
					  "Mrs. Sacko" : "CARLEN"}
	name_dict_2020 = {"Patrick is Ma Homie" : "MATT",
					  "Team Donked" : "STEVE",
					  "TOP DOG" : "DYLAN",
					  "The Legion of Poop" : "ANDREW",
					  "Fresh Princes of Bell-Aire" : "KYLE",
					  "'o o'" : "SAM",
					  "BHB: DO NOT RESUSCITATE" : "NICK",
					  "Botched Peen" : "NATHAN",
					  "Seattle WA Football Team" : "CHRIS",
					  "Bye Week" : "CARLEN"}
	name_dict_2021 = {"Dolphins Defense" : "MATT",
					  "TEAM GG NOT MY DAY" : "STEVE",
					  "New #10" : "DYLAN",
					  "The Legion of Mental Wellness" : "ANDREW",
					  "CMC + CC BUST" : "KYLE",
					  "'o o'" : "SAM",
					  "Daddy Suicide" : "NICK",
					  "Flacid Rage Quitters" : "NOAH",
					  "Loose Ends" : "CHRIS",
					  "Bishop Sycamore" : "JASON"}

	name_dict = name_dict_2014 | name_dict_2015 | name_dict_2016 | name_dict_2017 | name_dict_2018 | \
				name_dict_2019 | name_dict_2020 | name_dict_2021

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
league_id = "39598"
year_num = "2021"
year_length = 15

url_dict = get_week_urls(league_id, year_length, year_num)

score_dict[year_num] = get_scores(url_dict)
export(score_dict, f"ff_scores_{year_num}.csv")
