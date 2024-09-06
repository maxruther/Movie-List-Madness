USE moviedb;

DROP TABLE IF EXISTS Critic_Recommends;

CREATE TABLE IF NOT EXISTS Critic_recommends_og(
    Title varchar(40),
    Release_Date date,
    Director varchar(40),
    Watched int,
    Critic_recommending varchar(40),
    Rating varchar(40),
    Watched_in_theater int,
    Date_watched date,
    native_ordering int NOT NULL UNIQUE,
    
    PRIMARY KEY (Title, Director),
    CHECK (Watched in (0, 1)),
    CHECK (Watched_in_theater in (0, 1))
);

SELECT * FROM Backburning_classics;

-- CREATE TABLE IF NOT EXISTS Critic_recommends(Title varchar(40), Director varchar(40), Watched int, Critic_recommending varchar(40), Rating varchar(40), Date_watched date);
CREATE TABLE IF NOT EXISTS Critic_recommends(Title varchar(40), Release_Date date, Director varchar(40), Watched int, Critic_recommending varchar(40), Rating varchar(40), Watched_in_theater varchar(40), Date_watched date, CHECK (Watched in (0, 1)), CHECK (Watched_in_theater in (0, 1)));

CREATE TABLE IF NOT EXISTS Friend_Recommends(Title varchar(40), Director varchar(40), Watched int, Friend_recommending varchar(40), Rating varchar(40), Date_watched date);
DROP TABLE Critic_recommends_og;
INSERT INTO Critic_recommends_og VALUES ('The Barnacle Borough', 'Rockwell', 1, 'NYT', NULL, '2023-3-4', 0, NULL, 1000);
DELETE FROM Critic_recommends_og WHERE Title = 'The Barnacle Borough';
-- INSERT INTO Critic_recommends VALUES('Fallen Leaves', 'Kaurismaki', 0, 'NYT', NULL, NULL);
SELECT * FROM CRITIC_RECOMMENDS_og;
SELECT * FROM DRAMA;
INSERT INTO Drama VALUES('Aftersun', 'Wells', 1, NULL, '11-11-23');
-- SET SQL_SAFE_UPDATES = 0; 



SELECT * FROM Backburning_classics;
SELECT * FROM Drama WHERE Watched ORDER BY Release_Date DESC;
SELECT * FROM romance;

SHOW CREATE TABLE Critic_Recommends;

select COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_COLUMN_NAME, REFERENCED_TABLE_NAME
from information_schema.KEY_COLUMN_USAGE
where TABLE_NAME = 'Drama';

SELECT * FROM information_schemadrama WHERE TABLE_Name = "Drama";
DROP TABLE ANIMATE;
DROP TABLE MISC;
DROP TABLE MOVIES;

SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = "moviedb";


DROP TABLE IF EXISTS allWatched;
CREATE TABLE IF NOT EXISTS allWatched(
	Title varchar(40),
	Release_Date date,
	Director varchar(40),
	Watched int,
	Rating varchar(40),
	Date_watched date,
	native_ordering int NOT NULL,
	
	PRIMARY KEY (Title, Director),
	CHECK (Watched in (0, 1))
);

DEALLOCATE PREPARE getWatched;
SET @table = 'critic_recommends_og';
SET @b = CONCAT('INSERT INTO allWatched SELECT title, release_date, director, watched, rating, date_watched, native_ordering FROM ', @table, ' WHERE Watched = 1');
PREPARE getWatched FROM @b;
EXECUTE getWatched;
SELECT * FROM allWatched;



SELECT * FROM critic_recommends_og WHERE CONCAT(Title,Release_Date) IN (SELECT CONCAT(Title,Release_Date) FROM allWatched);

DROP TABLE critic_recommends_og;


SELECT * FROM allwatched;

-- Director tallies
SELECT director, count(*) FROM allWatched GROUP BY director ORDER BY count(*) DESC;