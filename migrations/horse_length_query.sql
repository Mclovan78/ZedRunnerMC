SELECT races.class, races.length, AVG(finish_time)
FROM races_results INNER JOIN races ON races_results.race_id=races.race_id WHERE races_results.horse_id = 24074
GROUP BY races.length, races.class ORDER BY races.class, races.length