USE movieDB;

DROP PROCEDURE IF EXISTS generateWatched;
DELIMITER //
CREATE PROCEDURE generateWatched()
BEGIN
	DECLARE done INT DEFAULT FALSE;
	DECLARE curr_table varchar(40) ;
    DECLARE table_cnt INT;
    DECLARE counter INT;
    DECLARE cur1 CURSOR FOR SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = "moviedb" and TABLE_NAME LIKE "%\_og";
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    SET table_cnt = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = "moviedb");
    
    DROP TABLE IF EXISTS allWatched;
	CREATE TABLE IF NOT EXISTS allWatched(
		Movie_ID int,
		Title varchar(40),
        Year varchar(40),
		Release_Date date,
		Director varchar(40),
		Watched int,
        Watched_in_theater int,
		Rating varchar(40),
		Date_watched date,
		native_ordering int NOT NULL,
		
		PRIMARY KEY (movie_id),
		CHECK (Watched in (0, 1))
	);
    
    OPEN cur1;
    SET counter = 0;
    read_loop: LOOP
		FETCH cur1 into curr_table;
        IF done THEN
			LEAVE read_loop;
		END IF;
                
        SET @table = curr_table;
        IF @table LIKE '%backburning%' THEN
			SET @b = CONCAT('INSERT INTO allWatched SELECT movie_id, title, year, release_date, director, watched, 0, rating, date_watched, native_ordering FROM ', @table, ' WHERE Watched = 1 AND CONCAT(Title,Director) NOT IN (SELECT CONCAT(Title,Director) FROM allWatched)');
		ELSE
			SET @b = CONCAT('INSERT INTO allWatched SELECT movie_id, title, year, release_date, director, watched, Watched_in_theater, rating, date_watched, native_ordering FROM ', @table, ' WHERE Watched = 1 AND CONCAT(Title,Director) NOT IN (SELECT CONCAT(Title,Director) FROM allWatched)');
		END IF;
        PREPARE getWatched FROM @b;
		EXECUTE getWatched;
	END LOOP;
END //
DELIMITER ;

SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = "moviedb" and TABLE_NAME LIKE "%\_og";
USE moviedb;
CALL generateWatched();

SELECT * FROM frontburners_og;

-- All watches, with latest at the top.
SELECT Title, Director, Release_Date, Rating, Date_watched FROM allWatched ORDER BY Date_watched DESC, Release_date DESC;

-- All in-theater watches, with latest at the top.
SELECT Title, Director, Release_Date, Rating, Date_watched FROM allWatched WHERE Watched_in_theater = 1 ORDER BY Date_watched DESC, Release_date DESC;

-- All watched titles, alphabetically.
SELECT * FROM allWatched ORDER BY Title ASC;

-- Highest rated watches, subordered by watch-date.
SELECT Title, Director, Release_Date, Rating, Date_watched,
	(
    CASE
		WHEN Rating = 'AWESOME' THEN 3
        WHEN RATING = 'PRETTY AWESOME' THEN 2
        WHEN Rating = 'GREAT' THEN 1
        ELSE 0
	END) AS RatingScore
FROM allWatched 
HAVING RatingScore > 0
ORDER BY RatingScore DESC, release_date DESC;
SELECT AM.title, AM.year, OD.year FROM allMovies AM, omdb_abrvd OD WHERE AM.title = OD.title and AM.year != OD.year;
SELECT AM.title, AM.year, OD.year FROM allMovies AM, omdb_abrvd OD WHERE AM.title = OD.title;
SELECT title FROM allMovies WHERE title not in (SELECT title FROM omdb_abrvd);
SELECT * FROM OMDB_abrvd;
SELECT * FROM omdb_abrvd where title LIKE "%poke%";
SELECT * FROM omdb_abrvd;

SELECT * FROM allwatched;