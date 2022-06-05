-- Create a database.
DROP DATABASE IF EXISTS mtgo_tracker_db;
CREATE DATABASE mtgo_tracker_db;
USE mtgo_tracker_db;

	-- SHOW VARIABLES LIKE "local_infile";
	-- SET GLOBAL local_infile = 1;

	-- Right click -> Edit connection -> Advanced -> Paste below in others box -> Test connection.
	-- OPT_local_infinite = 1;

-- Create a table.
DROP TABLE IF EXISTS drafts;
CREATE TABLE drafts (
	Draft_ID VARCHAR(75) NOT NULL,
    Hero VARCHAR(30) NOT NULL,
    Player_2 VARCHAR(30) NOT NULL,
    Player_3 VARCHAR(30) NOT NULL,
    Player_4 VARCHAR(30) NOT NULL,
    Player_5 VARCHAR(30) NOT NULL,
    Player_6 VARCHAR(30) NOT NULL,
    Player_7 VARCHAR(30) NOT NULL,
    Player_8 VARCHAR(30) NOT NULL,
    Match_Wins INT,
    Match_Losses INT,
    Format VARCHAR(18),
    Date VARCHAR(20),
	PRIMARY KEY (Draft_ID)
);

-- Create a table.
DROP TABLE IF EXISTS picks;
CREATE TABLE picks (
	Draft_ID VARCHAR(75) NOT NULL,
    Card VARCHAR(35) NOT NULL,
    Pack_Num INT,
    Pick_Num INT,
    Pick_Ovr INT,
    Avail_1 VARCHAR(35) NOT NULL,
    Avail_2 VARCHAR(35) NOT NULL,
    Avail_3 VARCHAR(35) NOT NULL,
    Avail_4 VARCHAR(35) NOT NULL,
    Avail_5 VARCHAR(35) NOT NULL,
    Avail_6 VARCHAR(35) NOT NULL,
    Avail_7 VARCHAR(35) NOT NULL,
    Avail_8 VARCHAR(35) NOT NULL,
    Avail_9 VARCHAR(35) NOT NULL,
    Avail_10 VARCHAR(35) NOT NULL,
    Avail_11 VARCHAR(35) NOT NULL,
    Avail_12 VARCHAR(35) NOT NULL,
    Avail_13 VARCHAR(35) NOT NULL,
    Avail_14 VARCHAR(35) NOT NULL,
	PRIMARY KEY (Draft_ID, Pick_Ovr),
    FOREIGN KEY (Draft_ID) REFERENCES drafts(Draft_ID)
);

-- Create a table.
DROP TABLE IF EXISTS matches_inverted;
CREATE TABLE matches_inverted (
	Match_ID VARCHAR(75) NOT NULL,
    Draft_ID VARCHAR(75) NOT NULL,
    P1 VARCHAR(30) NOT NULL,
    P1_Arch VARCHAR(15),
    P1_Subarch VARCHAR(30),
    P2 VARCHAR(30) NOT NULL,
    P2_Arch VARCHAR(15),
    P2_Subarch VARCHAR(30),
    P1_Roll INT,
    P2_Roll INT,
    Roll_Winner VARCHAR(2),
    P1_Wins INT,
    P2_Wins INT,
    Match_Winner VARCHAR(2),
    Format VARCHAR(20),
    Limited_Format VARCHAR(15),
    Match_Type VARCHAR(30),
    Date VARCHAR(20),
	PRIMARY KEY (Match_ID, P1),
    FOREIGN KEY (Draft_ID) REFERENCES drafts(Draft_ID)
);

-- Create a table.
DROP TABLE IF EXISTS matches;
CREATE TABLE matches (
	Match_ID VARCHAR(75) NOT NULL,
    Draft_ID VARCHAR(75) NOT NULL,
    P1 VARCHAR(30) NOT NULL,
    P1_Arch VARCHAR(15),
    P1_Subarch VARCHAR(30),
    P2 VARCHAR(30) NOT NULL,
    P2_Arch VARCHAR(15),
    P2_Subarch VARCHAR(30),
    P1_Roll INT,
    P2_Roll INT,
    Roll_Winner VARCHAR(2),
    P1_Wins INT,
    P2_Wins INT,
    Match_Winner VARCHAR(2),
    Format VARCHAR(20),
    Limited_Format VARCHAR(15),
    Match_Type VARCHAR(30),
    Date VARCHAR(20),
	PRIMARY KEY (Match_ID),
    FOREIGN KEY (Draft_ID) REFERENCES drafts(Draft_ID)
);

-- Create a table.
DROP TABLE IF EXISTS games_inverted;
CREATE TABLE games_inverted (
	Match_ID VARCHAR(75) NOT NULL,
    P1 VARCHAR(30) NOT NULL,
    P2 VARCHAR(30) NOT NULL,
    Game_Num INT,
    PD_Selector VARCHAR(2),
    PD_Choice VARCHAR(4),
    On_Play VARCHAR(2),
    On_Draw VARCHAR(2),
    P1_Mulls INT,
    P2_Mulls INT,
    Turns INT,
    Game_Winner VARCHAR(2),
	PRIMARY KEY (Match_ID, Game_Num, P1),
    FOREIGN KEY (Match_ID, P1) REFERENCES matches_inverted(Match_ID, P1)
);

-- Create a table.
DROP TABLE IF EXISTS games;
CREATE TABLE games (
	Match_ID VARCHAR(75) NOT NULL,
    P1 VARCHAR(30) NOT NULL,
    P2 VARCHAR(30) NOT NULL,
    Game_Num INT,
    PD_Selector VARCHAR(2),
    PD_Choice VARCHAR(4),
    On_Play VARCHAR(2),
    On_Draw VARCHAR(2),
    P1_Mulls INT,
    P2_Mulls INT,
    Turns INT,
    Game_Winner VARCHAR(2),
	PRIMARY KEY (Match_ID, Game_Num),
    FOREIGN KEY (Match_ID, P1) REFERENCES matches_inverted(Match_ID, P1)
);

-- Create a table.
DROP TABLE IF EXISTS plays;
CREATE TABLE plays (
	Match_ID VARCHAR(75) NOT NULL,
    Game_Num INT,
    Play_Num INT,
    Turn_Num INT,
    Casting_Player VARCHAR(30) NOT NULL,
    Action VARCHAR(20) NOT NULL,
	Primary_Card VARCHAR(35) NOT NULL,
    Target1 VARCHAR(35) NOT NULL,
    Target2 VARCHAR(35) NOT NULL,
    Target3 VARCHAR(35) NOT NULL,
    Opp_Target INT,
    Self_Target INT,
    Cards_Drawn INT,
    Attackers INT,
    Active_Player VARCHAR(30) NOT NULL,
    Nonactive_Player VARCHAR(30) NOT NULL,
	PRIMARY KEY (Match_ID, Game_Num, Play_Num),
    FOREIGN KEY (Match_ID, Game_Num) REFERENCES games(Match_ID, Game_Num),
    FOREIGN KEY (Match_ID) REFERENCES matches(Match_ID)
);

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTGO-Tracker/Drafts.csv"
INTO TABLE mtgo_tracker_db.drafts
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTGO-Tracker/Picks.csv"
INTO TABLE mtgo_tracker_db.picks
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- Skipping Foreign Key check because MySQL was giving a fake error when loading data from file.
SET FOREIGN_KEY_CHECKS = 0;

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTGO-Tracker/Matches_Inverted.csv"
INTO TABLE mtgo_tracker_db.matches_inverted
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTGO-Tracker/Matches.csv"
INTO TABLE mtgo_tracker_db.matches
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTGO-Tracker/Games_Inverted.csv"
INTO TABLE mtgo_tracker_db.games_inverted
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTGO-Tracker/Games.csv"
INTO TABLE mtgo_tracker_db.games
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTGO-Tracker/Plays.csv"
INTO TABLE mtgo_tracker_db.plays
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

SET FOREIGN_KEY_CHECKS = 1;