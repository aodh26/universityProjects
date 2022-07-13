DROP TABLE IF EXISTS scoreboard;

CREATE TABLE scoreboard 
(
    name TEXT PRIMARY KEY,
    score INTEGER NOT NULL
);

SELECT * 
FROM scoreboard;