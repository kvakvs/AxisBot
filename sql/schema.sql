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
-- ALTER TABLE outcomes ADD success integer DEFAULT false;

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

DROP TABLE IF EXISTS quotes;
CREATE TABLE IF NOT EXISTS quotes
(
    quote_key text PRIMARY KEY, -- short key to invoke the quote
    player_id integer,
    quote     text,             -- the quote
    UNIQUE (quote_key)
);

-----------------------------------------------------------------------
-- Professions
-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS item_cache
(
    item_id          integer PRIMARY KEY,
    item_name        text,
    wowhead_xml      text, -- wowhead XML of the recipe
    wowhead_stripped text, -- wowhead plain text of the recipe
    link             text, -- wowhead link to the recipe
    subclass         text  -- wowhead subclass field for the item type
);

CREATE TABLE IF NOT EXISTS craftables
(
    craftable_id integer PRIMARY KEY AUTOINCREMENT,
    player_id    integer, -- discord id of the player
    item_id      integer, -- fetches from wowhead or retrieves from item_cache
    FOREIGN KEY (item_id) REFERENCES item_cache (item_id)
);
