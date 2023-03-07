-----------------------------------------------------------------------
-- Players
-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS players
(
    player_id    integer PRIMARY KEY,
    discord_name text,
    display_name text,
    balance      integer
);

-----------------------------------------------------------------------
-- Events
-----------------------------------------------------------------------


CREATE TABLE IF NOT EXISTS events
(
    event_id   integer PRIMARY KEY AUTOINCREMENT,
    name       text,   -- event name
    author     text,   -- display name of the author
    channel_id integer,
    embed_id   integer -- the posted embed
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
    bet_id     integer PRIMARY KEY AUTOINCREMENT,
    player_id  integer,
    amount     integer,
    event_id   integer NOT NULL,
    outcome_id integer NOT NULL,
    UNIQUE (outcome_id, player_id), -- one outcome+player combination, multiple bets increase the amount
    FOREIGN KEY (event_id) REFERENCES events (event_id),
    FOREIGN KEY (outcome_id) REFERENCES outcomes (outcome_id)
);
