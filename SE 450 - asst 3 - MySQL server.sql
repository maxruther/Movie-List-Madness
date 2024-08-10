DROP TABLE IF EXISTS Fruits;

create table Fruits(
	name varchar(12),
    color varchar(12)
);

INSERT INTO Fruits VALUES( "Apple", "Red");
INSERT INTO Fruits VALUES( "Banana", "Yellow");

SELECT * FROM Fruits;

CREATE DATABASE javatestbase DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE USER 'java'@'localhost' IDENTIFIED BY 'password';
GRANT ALL ON javatestbase.* TO 'java'@'localhost';