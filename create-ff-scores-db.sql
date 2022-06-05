-- Create a database.
DROP DATABASE IF EXISTS ff_scores_db;
CREATE DATABASE ff_scores_db;
USE ff_scores_db;

	-- SHOW VARIABLES LIKE "local_infile";
	-- SET GLOBAL local_infile = 1;

	-- Right click -> Edit connection -> Advanced -> Paste below in others box -> Test connection.
	-- OPT_local_infinite = 1;

-- Create a table.
DROP TABLE IF EXISTS ff_scores;
CREATE TABLE ff_scores (
	year INT,
    week INT,
    team_1 VARCHAR(20) NOT NULL,
    team_1_score DECIMAL(5,2),
    team_2 VARCHAR(20) NOT NULL,
    team_2_score DECIMAL(5,2),
    win INT,
    reg INT,
    playoffs INT,
    champ_week INT,
    winner_rd_1 INT,
    loser_rd_1 INT,
    winner_rd_2 INT,
    loser_rd_2 INT,
    match_34 INT,
    match_56 INT,
    match_78 INT,
    match_12 INT,
    match_sacko INT,
    date VARCHAR(10),
	PRIMARY KEY (date, team_1, team_2)
);

-- Create a table.
DROP TABLE IF EXISTS ff_scores_inverted;
CREATE TABLE ff_scores_inverted (
	year INT,
    week INT,
    team_1 VARCHAR(20) NOT NULL,
    team_1_score DECIMAL(5,2),
    team_2 VARCHAR(20) NOT NULL,
    team_2_score DECIMAL(5,2),
    win INT,
    reg INT,
    playoffs INT,
    champ_week INT,
    winner_rd_1 INT,
    loser_rd_1 INT,
    winner_rd_2 INT,
    loser_rd_2 INT,
    match_34 INT,
    match_56 INT,
    match_78 INT,
    match_12 INT,
    match_sacko INT,
    date VARCHAR(10),
	PRIMARY KEY (date, team_1, team_2)
);

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/FFL/ff_scores.csv"
INTO TABLE ff_scores_db.ff_scores
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/FFL/ffscores_inverted.csv"
INTO TABLE ff_scores_db.ff_scores_inverted
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;