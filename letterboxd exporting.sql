USE movieDB;
SELECT * FROM omdb_abrvd;
SELECT * FROM allWatched ORDER BY Date_watched desc;
SELECT oa.Title, oa.Year, oa.Directors, DATE_FORMAT(aw.Date_watched, '%Y-%m-%d') as WatchedDate,
CASE
WHEN Rating = 'AWESOME' THEN 4.0
WHEN Rating = 'PRETTY AWESOME' THEN 3.5
WHEN Rating = 'GREAT' THEN 2.5
ELSE null
END AS Rating_nmrc
FROM omdb_abrvd as oa, allWatched as aw
WHERE oa.movie_ID = aw.movie_ID
ORDER BY Date_watched DESC;

SELECT * FROM ALLWATCHED ORDER BY Date_watched DESC;

SELECT * FROM ALLWATCHED WHERE Watched_in_theater ORDER BY Date_watched DESC;


SELECT oa.Title, oa.Year, oa.Directors, DATE_FORMAT(aw.Date_watched, '%Y-/%m-/%d'),
CASE
WHEN Rating = 'AWESOME' THEN 4.0
WHEN Rating = 'PRETTY AWESOME' THEN 3.5
WHEN Rating = 'GREAT' THEN 2.5
ELSE 0.5
END AS Rating_nmrc
FROM omdb_abrvd as oa, allWatched as aw
WHERE oa.movie_ID = aw.movie_ID
ORDER BY Date_watched DESC
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.2/Uploads/for_letterboxd.csv'
FIELDS TERMINATED BY ','
	OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

SHOW VARIABLES LIKE 'secure_file_priv';


SELECT oa.Title, oa.Year,aw.Release_Date, oa.Directors, DATE_FORMAT(aw.Date_watched, '%Y-%m-%d') as WatchedDate,
CASE
WHEN Rating = 'AWESOME' THEN 4.0
WHEN Rating = 'PRETTY AWESOME' THEN 3.5
WHEN Rating = 'GREAT' THEN 2.5
ELSE null
END AS Rating_nmrc
FROM omdb_abrvd as oa, allunwatched as aw
WHERE oa.movie_ID = aw.movie_ID
ORDER BY aw.Year DESC;

SELECT * FROM allunwatched;


SELECT oa.title,oa.year,oa.directors FROM faves_og as f, omdb_abrvd as oa
WHERE oa.movie_ID = f.movie_ID 
ORDER BY Release_Date asc;


use moviedb;
SELECT year, rating, count(*) FROM allwatched GROUP BY year, rating;

SELECT * FROM omdb_abrvd;

SELECT Movie_ID, Title, Year FROM allmovies;

SELECT * FROM animated_og;
SELECT * FROM allmovies;
SELECT * FROM critic_ratings;
