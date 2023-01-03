-- Create a database.
DROP DATABASE IF EXISTS lolesports_db;
CREATE DATABASE lolesports_db; 
USE lolesports_db;

-- REPLACE BLANK CELLS WITH /N
-- CREATE TABLE USING IMPORT WIZARD TO SET ROWS/DATATYPES
TRUNCATE lolesports_db.lolesports_2022;

	-- SHOW VARIABLES LIKE "local_infile";
SET GLOBAL local_infile = 1;

	-- Right click -> Edit connection -> Advanced -> Paste below in others box -> Test connection.
	-- OPT_local_infinite = 1;

	-- Use Import CSV Wizard to have columns set up, then cancel import.

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/LOL/lolesports_2022.csv"
INTO TABLE lolesports_db.lolesports_2022
FIELDS TERMINATED BY ","
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;