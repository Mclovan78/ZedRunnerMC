SELECT races.length, AVG(finish_time)
FROM races_results INNER JOIN races ON races_results.race_id=races.race_id 
INNER JOIN horses on horses.horse_id= races_results.horse_id 
GROUP BY races.length, horses.class

