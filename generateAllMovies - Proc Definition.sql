USE movieDB;

DROP PROCEDURE IF EXISTS generateAllMovies;

DELIMITER //
CREATE PROCEDURE generateAllMovies()
	
BEGIN
    
    DROP TABLE IF EXISTS allMovies;
    CREATE TABLE IF NOT EXISTS allMovies(
		movie_id int,
		Title varchar(40),
        Year varchar(40),
		Release_Date date,
		Director varchar(40),
		Watched int,
        Watched_in_theater int,
		Rating varchar(40),
		Date_watched date,
        Priority int,
		native_ordering int NOT NULL,
		
		PRIMARY KEY (movie_id),
		CHECK (Watched in (0, 1))
	);
    
    INSERT INTO allMovies (
    SELECT movie_id, title, year, release_date, director, watched, 0, rating, date_watched, priority, native_ordering FROM allunwatched
    UNION ALL
	SELECT movie_id, title, year, release_date, director, watched, watched_in_theater, rating, date_watched, 0, native_ordering FROM AllWatched
    );
    
END //
DELIMITER ;

CALL generateAllMovies();
SELECT * FROM allMovies ORDER BY movie_id ASC;
SELECT * FROM ALLUNWATCHED;
SELECT movie_id, title, year, release_date, director, watched, 0, rating, date_watched, priority, native_ordering FROM allunwatched;
SELECT movie_id, title, year, release_date, director, watched, watched_in_theater, rating, date_watched, 0, native_ordering FROM AllWatched;
SELECT movie_id, title, year, release_date, director, watched, watcher_in_theater, rating, date_watched, 0, native_ordering
SELECT * FROM Allwatched;


CREATE TABLE IF NOT EXISTS allMovies(
		movie_id int,
		Title varchar(40),
        Year varchar(40),
		Release_Date date,
		Director varchar(40),
		Watched int,
        Watched_in_theater int,
		Rating varchar(40),
		Date_watched date,
        Priority int,
		native_ordering int NOT NULL,
		
		PRIMARY KEY (movie_id),
		CHECK (Watched in (0, 1))
	);