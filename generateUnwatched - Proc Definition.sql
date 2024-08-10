USE movieDB;

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
		movie_id int,
		Title varchar(40),
        Year varchar(40),
		Release_Date date,
		Director varchar(40),
		Watched int,
		Rating varchar(40),
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
        
		SET @b = CONCAT('INSERT INTO allUnwatched SELECT movie_id, title, year, release_date, director, watched, rating, date_watched, ', p_rank, ', native_ordering FROM ', @table, ' WHERE Watched = 0 AND CONCAT(Title,Director) NOT IN (SELECT CONCAT(Title,Director) FROM allUnwatched)');
		PREPARE getUnwatched FROM @b;
		EXECUTE getUnwatched;
	END LOOP;
    
END //
DELIMITER ;

CALL generateUnwatched();
SELECT * FROM allUnwatched;

SELECT unw.title, fb.recommending, unw.release_date, unw.native_ordering 
FROM allUnwatched unw, frontburners_og fb 
WHERE unw.title = fb.Title
ORDER BY unw.release_date DESC;