-----------------------------------------------------------------------
-- Players
-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS players
(
    id      integer PRIMARY KEY,
    name    text,
    balance integer
);

-----------------------------------------------------------------------
-- Events
-----------------------------------------------------------------------


CREATE TABLE IF NOT EXISTS events
(
    event_id integer PRIMARY KEY AUTOINCREMENT,
    name     text,
    channel  integer
);

CREATE TABLE IF NOT EXISTS outcomes
(
    outcome_id integer PRIMARY KEY AUTOINCREMENT,
    event_id   integer NOT NULL,
    name       text,
    FOREIGN KEY (event_id) REFERENCES events (event_id)
);

CREATE TABLE IF NOT EXISTS bets
(
    id         integer PRIMARY KEY AUTOINCREMENT,
    player_id  integer,
    amount     integer,
    event_id   integer NOT NULL,
    outcome_id integer NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events (event_id),
    FOREIGN KEY (outcome_id) REFERENCES outcomes (outcome_id)
);
