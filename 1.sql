CREATE DATABASE vintage_db;
USE vintage_db;

CREATE TABLE vintage_events(
	event_id VARCHAR(30) PRIMARY KEY,
    event_type VARCHAR(20),
    event_date DATE,
    entries INT,
    day_of_week VARCHAR(9)
);

CREATE TABLE vintage_results(
	finish INT,
    player VARCHAR(30),
    wins INT,
    losses INT,
    byes INT,
    arch VARCHAR(30),
    subarch VARCHAR(30),
    deck VARCHAR(30),
    event_id VARCHAR(30),
    PRIMARY KEY (event_id, finish),
    FOREIGN KEY (event_id) REFERENCES vintage_events(event_id)
);

DROP TABLE vintage_events;

SELECT *
FROM vintage_events;

SELECT *
FROM vintage_results;