-- Create a database.
DROP DATABASE IF EXISTS chess_pgn_db;
CREATE DATABASE chess_pgn_db; 
USE chess_pgn_db;

	-- SHOW VARIABLES LIKE "local_infile";
	-- SET GLOBAL local_infile = 1;

	-- Right click -> Edit connection -> Advanced -> Paste below in others box -> Test connection.
	-- OPT_local_infinite = 1;

	-- Use Import CSV Wizard to have columns set up, then cancel import.

-- Load data from CSV.
LOAD DATA LOCAL INFILE "C:/Users/chris/Documents/Datasets/Chess PGN/pgn_move_records.csv"
INTO TABLE chess_pgn_db.pgn_move_records
FIELDS TERMINATED BY ","
IGNORE 1 ROWS;