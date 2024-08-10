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
SELECT * FROM allunWatched;


SELECT * FROM critic_recommends_og WHEREs CONCAT(Title,Release_Date) IN (SELECT CONCAT(Title,Release_Date) FROM allWatched);

DROP TABLE critic_recommends_og;


SELECT * FROM allwatched;

-- Director tallies
SELECT director, count(*) FROM allWatched GROUP BY director ORDER BY count(*) DESC;

CREATE TABLE allMovies AS SELECT * FROM (
	SELECT * FROM allWatched
	UNION ALL
	SELECT * FROM allUnwatched
) as allFilms;
SELECT * FROM allMovies ORDER BY Title asc;
SELECT Watched, Watched_in_theater, count(*) FROM allMovies GROUP BY Watched, Watched_in_theater;
SELECT * FROM allMovies WHERE Watched_in_theater = " ";

SELECT Title, YEAR(release_date) as Year FROM allMovies LIMIT 5;

DROP TABLE IF EXISTS critic_ratings;
CREATE TABLE IF NOT EXISTS critic_ratings(
	Title varchar(80),
    Year varchar(80),
    IMDB_Score float,
    RT_Score float,
    MetaC_Score float
    );

select title, year from allmovies where title = 'room';

SELECT * FROM critic_ratings ORDER BY MetaC_Score DESC, IMDB_Score DESC;
SELECT * FROM allmovies WHERE title LIKE "%room%";

SELECT aw.title, date_watched, rating, imdb_score, rt_score, metac_score 
FROM allWatched AW, critic_ratings CR 
WHERE AW.title = CR.title and AW.year = CR.year
ORDER BY rating ASC, metac_score DESC;


CREATE TABLE IF NOT EXISTS allMovsGenres(
	Title varchar(80),
    Year varchar(80),
    Comedy int,
    Drama int,
    Action int,
    Adventure int,
    Romance int,
    Family int,
    Animation int,
    Documentary int,
    Thriller int,
    SciFi int,
    Horror int,
    Mystery int,
    Fantasy int,
    Biography int,
    History int,
    Crime int,
    Music int,
    Short int,
    War int,
    Western int,
    Sport int,
    
    PRIMARY KEY (Title, Year),
    CHECK (Comedy in (0, 1)), 
    CHECK (Drama in (0, 1)), 
    CHECK (Action in (0, 1)), 
    CHECK (Adventure in (0, 1)), 
    CHECK (Romance in (0, 1)), 
    CHECK (Family in (0, 1)), 
    CHECK (Animation in (0, 1)), 
    CHECK (Documentary in (0, 1)),
    CHECK (Thriller in (0, 1)), 
    CHECK (Sci-Fi in (0, 1)), 
    CHECK (Horror in (0, 1)), 
    CHECK (Mystery in (0, 1)), 
    CHECK (Fantasy in (0, 1)), 
    CHECK (Biography in (0, 1)), 
    CHECK (History in (0, 1)), 
    CHECK (Crime in (0, 1)), 
    CHECK (Music in (0, 1)), 
    CHECK (Short in (0, 1)), 
    CHECK (War in (0, 1)), 
    CHECK (Western in (0, 1)), 
    CHECK (Sport in (0, 1))
    );
    
CREATE TABLE IF NOT EXISTS allMovsGenres(Title varchar(80), Year varchar(80), Comedy int, Drama int, Action int, Adventure int, Romance int, Family int, Animation int, Documentary int, Thriller int, SciFi int, Horror int, Mystery int, Fantasy int, Biography int, History int, Crime int, Music int, Short int, War int, Western int, Sport int, PRIMARY KEY (Title, Year), CHECK (Comedy in (0, 1)), CHECK (Drama in (0, 1)), CHECK (Action in (0, 1)), CHECK (Adventure in (0, 1)), CHECK (Romance in (0, 1)), CHECK (Family in (0, 1)), CHECK (Animation in (0, 1)), CHECK (Documentary in (0, 1)), CHECK (Thriller in (0, 1)), CHECK (SciFi in (0, 1)), CHECK (Horror in (0, 1)), CHECK (Mystery in (0, 1)), CHECK (Fantasy in (0, 1)), CHECK (Biography in (0, 1)), CHECK (History in (0, 1)), CHECK (Crime in (0, 1)), CHECK (Music in (0, 1)), CHECK (Short in (0, 1)), CHECK (War in (0, 1)), CHECK (Western in (0, 1)), CHECK (Sport in (0, 1)));

USE moviedb;

SELECT * FROM allMovsGenres;
SELECT * FROM allMovsGenres WHERE Biography;
SELECT sum(action), sum(thriller), sum(drama), sum(horror), sum(crime), sum(comedy), sum(fantasy), sum(adventure), sum(romance), sum(scifi), sum(war), sum(animation), sum(family) FROM allMovsGenres;  

SELECT USER FROM mysql.user;
SELECT * FROM Allwatched ORDER BY Date_Watched DESC;

SELECT * FROM AllMovies AM1, AllMovies AM2 WHERE AM1.movie_id = AM2.movie_id AND AM1.Native_ordering != AM2.Native_ordering ORDER BY AM1.movie_id ASC ;

DROP TABLE IF EXISTS critic_ratings;
CREATE TABLE IF NOT EXISTS critic_ratings(
	Movie_ID int NOT NULL,
	Title varchar(80),
    Year varchar(80),
    IMDB_Score float,
    RT_Score float,
    MetaC_Score float,
    
    FOREIGN KEY(Movie_ID) REFERENCES allmovies(movie_id)
    );
SELECT * FROM allmovies;
SELECT * FROM critic_ratings;

SELECT * FROM omdb_abrvd;

DROP TABLE omdb_abrvd;
CREATE TABLE IF NOT EXISTS omdb_abrvd(Movie_ID int, Title varchar(80), Year varchar(80), OMDB_Release varchar(80), Runtime int, Genres varchar(80), Directors varchar(80), Writers varchar(80), Actors varchar(80), IMDB_Score float, RT_Score float, MetaC_Score float, Earnings int,  PRIMARY KEY(Movie_ID));
SELECT * FROM omdb_abrvd;

DROP TABLE allMovsGenres;
CREATE TABLE IF NOT EXISTS allMovsGenres(Movie_ID int, Title varchar(80), Year varchar(80), Action int, Thriller int, Comedy int, Drama int, Horror int, Mystery int, Crime int, Documentary int, Fantasy int, Adventure int, Romance int, SciFi int, War int, Music int, Animation int, Sport int, History int, Family int, Biography int, Western int, Short int, FOREIGN KEY(Movie_ID) REFERENCES allmovies(Movie_ID), CHECK (Action in (0, 1)), CHECK (Thriller in (0, 1)), CHECK (Comedy in (0, 1)), CHECK (Drama in (0, 1)), CHECK (Horror in (0, 1)), CHECK (Mystery in (0, 1)), CHECK (Crime in (0, 1)), CHECK (Documentary in (0, 1)), CHECK (Fantasy in (0, 1)), CHECK (Adventure in (0, 1)), CHECK (Romance in (0, 1)), CHECK (SciFi in (0, 1)), CHECK (War in (0, 1)), CHECK (Music in (0, 1)), CHECK (Animation in (0, 1)), CHECK (Sport in (0, 1)), CHECK (History in (0, 1)), CHECK (Family in (0, 1)), CHECK (Biography in (0, 1)), CHECK (Western in (0, 1)), CHECK (Short in (0, 1)));
SELECT * FROM allMovsGenres;
SELECT * FROM omdb_abrvd;
SELECT * FROM critic_ratings;

-- Unwatched releases from the past two years, ordered by metacritic score.
SELECT un.priority, un.title, un.director, un.release_date, om.runtime, om.metaC_score, om.imdb_score 
from allunwatched un, omdb_abrvd om 
where un.movie_id=om.movie_id AND year(un.release_date) > 2021
ORDER BY metac_score desc, imdb_score desc;

SELECT un.priority, un.title, un.director, un.release_date, om.runtime, om.metaC_score, om.imdb_score 
from allunwatched un, omdb_abrvd om 
where un.movie_id=om.movie_id AND year(un.release_date) > 2021
ORDER BY runtime ASC;

USE moviedb;
SELECT * FROM omdb_abrvd;
SELECT * FROM allwatched ORDER BY date_watched DESC;

SELECT aw.movie_id, aw.title, aw.year, aw.release_date, aw.director, aw.watched_in_theater, aw.rating, aw.date_watched,
om.runtime, om.imdb_score, om.rt_score, om.metac_score, om.earnings
FROM allmovies aw, omdb_abrvd om
WHERE aw.movie_id = om.movie_id
ORDER BY date_watched DESC;

SELECT *  
FROM allmovies aw, omdb_abrvd om
WHERE aw.movie_id = om.movie_id and aw.TITLE="Skinamarink";

SELECT * FROM allunwatched;