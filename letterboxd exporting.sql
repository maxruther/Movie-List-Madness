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
SELECT * FROM allmovies;
SELECT * FROM omdb_abrvd;
SELECT * FROM allwatched;

SELECT * FROM allwatched ORDER BY Date_watched DESC;
SELECT * FROM allmovies WHERE Release_Date IS NULL;

# Checking that allwatched has the same count as that of watched movies from allmovies.
SELECT COUNT(*) FROM allmovies WHERE Watched;
SELECT COUNT(*) FROM allwatched;

ALTER TABLE critic_ratings RENAME INDEX index TO Movie_ID;

SELECT * FROM critic_ratings WHERE Title = "Outlaw Johnny Black";

SELECT * FROM critic_ratings c inner join allmovies a on c.Title = a.Title;


SELECT Title,Year FROM critic_ratings where Title not in (SELECT Title from allmovies)
UNION
(SELECT Title,Year FROM allmovies where Title NOT IN (SELECT Title from critic_ratings));
SELECT * FROM critic_ratings; SELECT * FROM allmovies;



SELECT c.Movie_ID, c.Title, c.Year, c.MetaC_Score, a.Release_Date 
FROM critic_ratings c INNER JOIN allmovies a ON c.Title=a.Title
WHERE c.MetaC_Score IS NULL
ORDER BY a.Release_Date ASC;

SELECT Movie_ID, Title FROM
(SELECT c.Movie_ID, c.Title, c.Year, c.RT_Score, a.Release_Date 
FROM critic_ratings c INNER JOIN allmovies a ON c.Title=a.Title
WHERE c.RT_Score IS NULL
ORDER BY a.Release_Date ASC) AS tt;

SELECT Movie_ID, Title FROM 
(SELECT c.Movie_ID, c.Title, c.Year, c.MetaC_Score, a.Release_Date 
FROM critic_ratings c INNER JOIN allmovies a 
ON c.Title=a.Title 
WHERE c.MetaC_Score IS NULL
ORDER BY a.Release_Date ASC) AS tt;

SELECT * FROM critic_ratings c INNER JOIN allwatched aw ON c.Title=aw.Title ORDER BY MetaC_Score DESC;
SELECT * FROM critic_ratings c INNER JOIN allwatched aw ON c.Title=aw.Title WHERE MetaC_Score IS NULL ORDER BY aw.Release_Date DESC;

SELECT Movie_ID, Title, Year FROM allmovies;


SELECT * FROM allmovsgenres;
SELECT * FROM allmovies;
SELECT * FROM omdb_abrvd;
SELECT * FROM allmovies;
 SELECT * FROM allunwatched ORDER BY Movie_ID;
 
 CREATE TABLE IF NOT EXISTS KissMyDick_og(
 ID int
 );
 INSERT INTO KissMyDick_og VALUES (1);
 SELECT * FROM KissMyDick_og;
 
 SELECT * FROM frontburners_og;
 
SELECT Title, Director FROM comedies_og WHERE Watched = 1 AND CONCAT(Title,Director) NOT IN (SELECT CONCAT(Title,Director) FROM allWatched);
SELECT * FROM comedies_og;
SELECT * FROM drama_og;
SELECT * FROM horror_og;
SELECT CONCAT(Title,Director) FROM comedies_og WHERE Movie_ID=16;
SELECT CONCAT(Title,Director) FROM allWatched;
SELECT * FROM allwatched;
SELECT * FROM allwatched WHERE title=;

SELECT Movie_ID, title, year, release_date, director, watched, 0, rating, date_watched, native_ordering FROM drama_og WHERE Watched = 1;
SELECT * FROM allmovies;

SELECT * FROM allunwatched;
SELECT * FROM allwatched;

SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = "moviedb"  and TABLE_NAME LIKE "%\_og";

SELECT * FROM allunwatched
UNION ALL
SELECT * FROM allwatched
ORDER BY Movie_ID;

DROP TABLE IF EXISTS allwatched;
DROP TABLE IF EXISTS allunwatched;

SELECT * FROM critic_ratings;