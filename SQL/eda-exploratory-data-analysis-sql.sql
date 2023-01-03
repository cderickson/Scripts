-- Number of columns, rows in a table.
SELECT
	(SELECT count(*) AS numRows
	FROM ff_scores_db.ff_scores) AS row_count,
	(SELECT count(*) AS numCols
	FROM information_schema.columns
	WHERE table_name = "ff_scores") AS col_count;

-- Unique values in a specified column.
SELECT DISTINCT week
FROM ff_scores_db.ff_scores;

-- Return rows with Null in a specified row.
SELECT *
FROM ff_scores_db.ff_scores
WHERE (week IS NULL) or (week = "");

-- Descriptive statistics for a specified column.
SELECT sum(team_1_score) AS team_1_score
FROM ff_scores_db.ff_scores
UNION
SELECT avg(team_1_score)
FROM ff_scores_db.ff_scores
UNION
SELECT min(team_1_score)
FROM ff_scores_db.ff_scores
UNION
SELECT max(team_1_score)
FROM ff_scores_db.ff_scores;