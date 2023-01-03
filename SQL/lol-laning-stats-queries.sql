SELECT teamname, sum(result) AS wins,
	sum(CASE
		WHEN result = 0 THEN 1
        ELSE 0
	END) AS losses
FROM lolesports_db.lolesports_2022
WHERE participantid > 10 AND league = 'LCS'
GROUP BY teamname;

SELECT champion, sum(pentakills) AS penta_cnt
FROM lolesports_db.lolesports_2022
WHERE participantid <= 10
GROUP BY champion
HAVING penta_cnt > 0
ORDER BY penta_cnt DESC;

CREATE VIEW lolesports_db.laning_stats_by_champ_2022 AS
SELECT 
	t1.gameid, t1.league, t1.teamname, t1.patch , t1.side, t1.position, t1.playername, t1.champion, 
    t2.side AS opp_side, t2.playername AS opp_playername, t2.champion AS opp_champion,
    t1.goldat10, t1.xpat10, t1.csat10, 
    t1.opp_goldat10, t1.opp_xpat10, t1.opp_csat10, 
    t1.golddiffat10, t1.xpdiffat10, t1.csdiffat10, 
    t1.killsat10, t1.assistsat10, t1.deathsat10, 
    t1.opp_killsat10, t1.opp_assistsat10, t1.opp_deathsat10,
    t1.goldat15, t1.xpat15, t1.csat15, 
    t1.opp_goldat15, t1.opp_xpat15, t1.opp_csat15, 
    t1.golddiffat15, t1.xpdiffat15, t1.csdiffat15, 
    t1.killsat15, t1.assistsat15, t1.deathsat15, 
    t1.opp_killsat15, t1.opp_assistsat15, t1.opp_deathsat15, t1.result
FROM lolesports_db.lolesports_2022 t1 JOIN lolesports_db.lolesports_2022 t2
ON t1.gameid = t2.gameid AND t1.position = t2.position AND t1.side <> t2.side
WHERE t1.position <> 'team' AND t1.datacompleteness = 'complete';

SELECT *
FROM lolesports_db.lolesports_2022;