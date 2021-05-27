SELECT races.class, races.length, AVG(finish_time)
FROM races_results INNER JOIN races ON races_results.race_id=races.race_id
GROUP BY races.length, races.class ORDER BY races.class, races.length
