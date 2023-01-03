-- Create a database.
DROP DATABASE IF EXISTS vintage_metagame_db;
CREATE DATABASE vintage_metagame_db;
USE vintage_metagame_db;

	-- SHOW VARIABLES LIKE "local_infile";
	-- SET GLOBAL local_infile = 1;

	-- Right click -> Edit connection -> Advanced -> Paste below in others box -> Test connection.
	-- OPT_local_infinite = 1;

-- Create a table.
DROP TABLE IF EXISTS vintage_events;
CREATE TABLE vintage_events (
	Event_ID VARCHAR(50) NOT NULL,
    Event_Type VARCHAR(30) NOT NULL,
    Event_Date DATE NOT NULL,
    Entries INT DEFAULT 0,
    Day_Of_Week VARCHAR(9) NOT NULL,
	PRIMARY KEY (Event_ID)
);

-- Create a table.
DROP TABLE IF EXISTS vintage_results;
CREATE TABLE vintage_results (
	Finish INT DEFAULT 0,
    Player VARCHAR(30) NOT NULL,
    Wins INT DEFAULT 0,
    Losses INT DEFAULT 0,
    Byes INT DEFAULT 0,
    Arch VARCHAR(30) DEFAULT NULL,
    Subarch VARCHAR(30) DEFAULT NULL,
    Deck VARCHAR(50) DEFAULT NULL,
    Event_ID VARCHAR(50) NOT NULL,
	PRIMARY KEY (Event_ID, Finish),
    FOREIGN KEY (Event_ID) REFERENCES vintage_events(Event_ID)
);

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTG Vintage/vintage-events.csv"
INTO TABLE vintage_metagame_db.vintage_events
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- Skipping Foreign Key check because MySQL was giving a fake error when loading data from file.
SET FOREIGN_KEY_CHECKS = 0;
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTG Vintage/vintage-results.csv"
INTO TABLE vintage_metagame_db.vintage_results
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;
SET FOREIGN_KEY_CHECKS = 1;