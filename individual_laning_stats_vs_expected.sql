SELECT position, playername, teamname, league, count(*) AS games_played,
	round(avg(gd10_oe),0) AS avg_gd10_oe, round(avg(xpd10_oe),0) AS avg_xpd10_oe, round(avg(csd10_oe),0) AS avg_csd10_oe, 
	round(avg(gd15_oe),0) AS avg_gd15_oe, round(avg(xpd15_oe),0) AS avg_xpd15_oe, round(avg(csd15_oe),0) AS avg_csd15_oe
FROM lolesports_db.laning_stats_over_expected
GROUP BY playername, league, position
ORDER BY league ASC, position ASC, avg_gd10_oe DESC