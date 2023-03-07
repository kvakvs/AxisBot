import sqlite3


def init_db():
    conn = sqlite3.connect("axisbot.db")
    # c = conn.cursor()
    # c.execute(open("sql/schema.sql", encoding='utf-8-sig').read())
    # conn.commit()

    return conn


EVENTS = init_db()


def add_ulduar_event(name: str, channel: int):
    global EVENTS
    EVENTS.execute("INSERT INTO events(name, channel) VALUES(?, ?)", (name, channel,))
    EVENTS.commit()

    event_id = EVENTS.execute("SELECT last_insert_rowid()").fetchone()[0]

    for boss in ["Flame Leviathan", "Ignis", "Razorscale", "XT-002",
                 "Assembly of Iron", "Kologarn", "Auriaya", "Mimiron", "Hodir", "Thorim", "Freya",
                 "Vezax", "Algalon"]:
        EVENTS.execute("INSERT INTO outcomes(event_id, name) VALUES(?, ?)", (event_id, boss,))

    EVENTS.commit()
