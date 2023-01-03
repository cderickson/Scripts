DROP VIEW IF EXISTS mtgo_tracker_db.card_winrates;
CREATE VIEW mtgo_tracker_db.card_winrates AS
SELECT 
	Primary_Card, 
    ROUND((Wins/(Wins + Losses)), 3) AS Win_Rate, 
    (Wins + Losses) AS Total_Games, 
    ROUND((Pre_SB_Wins/(Pre_SB_Wins + Pre_SB_Losses)), 3) AS Pre_SB_Win_Rate,
    (Pre_SB_Wins + Pre_SB_Losses) AS Pre_SB_Games,
    ROUND((Post_SB_Wins/(Post_SB_Wins + Post_SB_Losses)), 3) AS Post_SB_Win_Rate,
    (Post_SB_Wins + Post_SB_Losses) AS Post_SB_Games
FROM (
	SELECT 
		Primary_Card,
		COUNT(CASE 
			WHEN (P1 = Casting_Player) AND (Game_Winner = "P1") THEN 1
			WHEN (P2 = Casting_Player) AND (Game_Winner = "P2") THEN 1
			ELSE NULL 
		END) AS Wins,
		COUNT(CASE 
			WHEN (P1 = Casting_Player) AND (Game_Winner) = "P2" THEN 1
			WHEN (P2 = Casting_Player) AND (Game_Winner) = "P1" THEN 1
			ELSE NULL 
		END) AS Losses,
		COUNT(CASE 
			WHEN (P1 = Casting_Player) AND (Game_Winner = "P1") AND (Game_Num = 1) THEN 1
			WHEN (P2 = Casting_Player) AND (Game_Winner = "P2") AND (Game_Num = 1) THEN 1
			ELSE NULL 
		END) AS Pre_SB_Wins,
		COUNT(CASE 
			WHEN (P1 = Casting_Player) AND (Game_Winner = "P2") AND (Game_Num = 1) THEN 1
			WHEN (P2 = Casting_Player) AND (Game_Winner = "P1") AND (Game_Num = 1) THEN 1
			ELSE NULL 
		END) AS Pre_SB_Losses,
		COUNT(CASE 
			WHEN (P1 = Casting_Player) AND (Game_Winner = "P1") AND (Game_Num > 1) THEN 1
			WHEN (P2 = Casting_Player) AND (Game_Winner = "P2") AND (Game_Num > 1) THEN 1
			ELSE NULL 
		END) AS Post_SB_Wins,
		COUNT(CASE 
			WHEN (P1 = Casting_Player) AND (Game_Winner = "P2") AND (Game_Num > 1) THEN 1
			WHEN (P2 = Casting_Player) AND (Game_Winner = "P1") AND (Game_Num > 1) THEN 1
			ELSE NULL 
		END) AS Post_SB_Losses
	FROM mtgo_tracker_db.matches m JOIN mtgo_tracker_db.games g
	USING (Match_ID, P1, P2)
	JOIN mtgo_tracker_db.plays p
	USING (Match_ID, Game_Num)
	WHERE Action IN ("Casts", "Land Drop")
	GROUP BY Primary_Card
) AS t
ORDER BY Total_Games DESC