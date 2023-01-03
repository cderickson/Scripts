CREATE VIEW lolesports_db.laning_stats_over_expected AS
SELECT t1.patch, t1.position, t1.playername, t1.league, t1.teamname, t1.champion, t1.opp_playername, t1.opp_champion, 
    (t1.golddiffat10 - t2.avg_golddiffat10) AS gd10_oe, (t1.xpdiffat10 - t2.avg_xpdiffat10) AS xpd10_oe, (t1.csdiffat10 - t2.avg_csdiffat10) AS csd10_oe,
    (t1.golddiffat15 - t2.avg_golddiffat15) AS gd15_oe, (t1.xpdiffat15 - t2.avg_xpdiffat15) AS xpd15_oe, (t1.csdiffat15 - t2.avg_csdiffat15) AS csd15_oe
FROM lolesports_db.laning_stats_by_champ_2022 t1 JOIN lolesports_db.lane_matchup_avgs t2
ON t1.position = t2.position AND t1.champion = t2.champion AND t1.opp_champion = t2.opp_champion AND t1.patch = t2.patch