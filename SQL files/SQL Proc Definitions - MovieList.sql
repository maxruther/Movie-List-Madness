USE movieDB;


# Create the table of watched movies, 'allwatched'

# NOTE: This procedure ERRORS if there are existing tables with '_og' in their 
# name that don't correspond to a table in the Evernote movie list.
# (This issue was encountered on 8-14-2024)

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
		Title varchar(80),
        Year varchar(80),
		Release_Date date,
		Director varchar(80),
		Watched int,
        Watched_in_theater int,
		Rating varchar(80),
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
			SET @b = CONCAT('INSERT INTO allWatched SELECT movie_id, title, year, release_date, director, watched, 0, rating, date_watched, native_ordering FROM ', @table, ' WHERE Watched = 1 AND movie_id NOT IN (SELECT movie_id FROM allWatched)');
		ELSE
			SET @b = CONCAT('INSERT INTO allWatched SELECT movie_id, title, year, release_date, director, watched, Watched_in_theater, rating, date_watched, native_ordering FROM ', @table, ' WHERE Watched = 1 AND movie_id NOT IN (SELECT movie_id FROM allWatched)');
		END IF;
        PREPARE getWatched FROM @b;
		EXECUTE getWatched;
	END LOOP;
END //
DELIMITER ;



# Create the table of unwatched movies, 'allunwatched'.

# NOTE: This procedure ERRORS if there are existing tables with '_og' in their 
# name that don't correspond to a table in the Evernote movie list.
# (This issue was encountered on 8-14-2024)

DROP PROCEDURE IF EXISTS generateUnwatched;

DELIMITER //
CREATE PROCEDURE generateUnwatched()
BEGIN
	DECLARE done INT DEFAULT FALSE;
	DECLARE curr_table varchar(40) ;
    DECLARE table_cnt INT;
    DECLARE counter INT;
    DECLARE p_rank int;
    DECLARE cur1 CURSOR FOR SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = "moviedb" and TABLE_NAME LIKE "%\_og";
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    SET table_cnt = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = "moviedb"  and TABLE_NAME LIKE "%\_og");
    
    DROP TABLE IF EXISTS allUnwatched;
	CREATE TABLE IF NOT EXISTS allUnwatched(
		Movie_ID int,
		Title varchar(80),
        Year varchar(80),
		Release_Date date,
		Director varchar(80),
		Watched int,
		Rating varchar(80),
		Date_watched date,
        Priority int,
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
        
        IF (@table LIKE '%frontburner%') THEN
			SET p_rank = 1;
		ELSEIF (@table LIKE '%critic_backburners%') THEN
			SET p_rank = 2;
		ELSEIF (@table LIKE '%friend_recommends%') THEN
			SET p_rank = 4;
		ELSEIF (@table LIKE '%podcast_recommends%') THEN
			SET p_rank = 5;
		ELSEIF (@table LIKE '%backburning_classics%') THEN
			SET p_rank = 6;
		ELSEIF (@table LIKE '%backburning_misc%') THEN
			SET p_rank = 7;
		ELSE
			SET p_rank = 3;
		END IF;
        
		SET @b = CONCAT('INSERT INTO allUnwatched SELECT movie_id, title, year, release_date, director, watched, rating, date_watched, ', p_rank, ', native_ordering FROM ', @table, ' WHERE Watched = 0 AND Movie_ID NOT IN (SELECT Movie_ID FROM allUnwatched)');
		PREPARE getUnwatched FROM @b;
		EXECUTE getUnwatched;
	END LOOP;
    
END //
DELIMITER ;



# Creates the table of all movies, 'allmovies'.

DROP PROCEDURE IF EXISTS generateAllMovies;

DELIMITER //
CREATE PROCEDURE generateAllMovies()
	
BEGIN
    
    DROP TABLE IF EXISTS allMovies;
    CREATE TABLE IF NOT EXISTS allMovies(
		Movie_ID int,
		Title varchar(80),
        Year varchar(80),
		Release_Date date,
		Director varchar(80),
		Watched int,
        Watched_in_theater int,
		Rating varchar(80),
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


