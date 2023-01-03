DROP VIEW IF EXISTS mtgo_tracker_db.sideboard_view;
CREATE VIEW mtgo_tracker_db.sideboard_view AS
SELECT 
	CASE WHEN Game_Num = 1 THEN "Pre-Sideboard"
		 WHEN Game_Num > 1 THEN "Post-Sideboard"
		 ELSE NULL 
	END AS Sideboard,
	P1, P1_Subarch, P2, P2_Subarch, On_Play, On_Draw, P1_Mulls, P2_Mulls, Play_Num,
	CASE WHEN Casting_Player = P1 THEN "P1"
		 WHEN Casting_Player = P2 THEN "P2"
		 ELSE NULL 
	END AS Casting_Player,
	Action, Primary_Card, Target1, Date
FROM mtgo_tracker_db.matches m JOIN mtgo_tracker_db.games g
USING (Match_ID, P1, P2)
JOIN mtgo_tracker_db.plays p
USING (Match_ID, Game_Num)
WHERE Action IN ("Casts", "Land Drop")
ORDER BY Date DESC