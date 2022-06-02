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
	event_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(30) NOT NULL,
    event_date DATE NOT NULL,
    entries INT DEFAULT 0,
    day_of_week VARCHAR(9) NOT NULL,
	PRIMARY KEY (event_id)
);

-- Create a table.
DROP TABLE IF EXISTS vintage_results;
CREATE TABLE vintage_results (
	finish INT DEFAULT 0,
    player VARCHAR(30) NOT NULL,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    byes INT DEFAULT 0,
    arch VARCHAR(30) DEFAULT NULL,
    subarch VARCHAR(30) DEFAULT NULL,
    deck VARCHAR(50) DEFAULT NULL,
    event_id VARCHAR(50) NOT NULL,
	PRIMARY KEY (event_id, finish),
    FOREIGN KEY (event_id) REFERENCES vintage_events(event_id)
);

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTG Vintage/vintage-events.csv"
INTO TABLE vintage_metagame_db.vintage_events
FIELDS TERMINATED BY ","
IGNORE 1 ROWS;

-- Skipping Foreign Key check because MySQL was giving a fake error when loading data from file.
SET FOREIGN_KEY_CHECKS = 0;
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/MTG Vintage/vintage-results.csv"
INTO TABLE vintage_metagame_db.vintage_results
FIELDS TERMINATED BY ","
IGNORE 1 ROWS;
SET FOREIGN_KEY_CHECKS = 1;