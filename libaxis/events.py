import sqlite3
from typing import Optional

import discord


def init_db():
    conn = sqlite3.connect("axisbot.db")
    # c = conn.cursor()
    # c.execute(open("sql/schema.sql", encoding='utf-8-sig').read())
    # conn.commit()

    return conn


EVENTS = init_db()


class Event:
    def __init__(self, event_id: int, name: str, author: str, channel_id: int, embed_id: Optional[int] = None):
        self.event_id = event_id
        self.name = name
        self.author = author
        self.channel_id = channel_id
        self.embed_id = embed_id

    def get_pot(self) -> int:
        global EVENTS
        c = EVENTS.cursor()
        c.execute("SELECT SUM(amount) FROM bets WHERE event_id = ?", (self.event_id,))
        result = c.fetchone()
        return result[0] if result is not None else 0


def event_from_id(event_id: int) -> Event:
    global EVENTS
    c = EVENTS.cursor()
    c.execute("SELECT event_id, name, author, channel_id, embed_id "
              "FROM events WHERE event_id = ?", (event_id,))
    result = c.fetchone()
    return Event(event_id=result[0],
                 name=result[1],
                 author=result[2],
                 channel_id=result[3],
                 embed_id=result[4]) if result is not None else None


class Outcome:
    def __init__(self, outcome_id: int, event_id: int, name: str):
        self.outcome_id = outcome_id
        self.event_id = event_id
        self.name = name


def outcome_from_id(outcome_id: int) -> Outcome:
    global EVENTS
    c = EVENTS.cursor()
    c.execute("SELECT outcome_id, event_id, name "
              "FROM outcomes WHERE outcome_id = ?", (outcome_id,))
    result = c.fetchone()
    return Outcome(outcome_id=result[0],
                   event_id=result[1],
                   name=result[2]) if result is not None else None


def get_outcomes(event_id: int) -> list[Outcome]:
    global EVENTS
    c = EVENTS.cursor()
    c.execute("SELECT outcome_id, event_id, name "
              "FROM outcomes WHERE event_id = ? ORDER BY outcome_id", (event_id,))
    result = c.fetchall()
    return [Outcome(outcome_id=row[0],
                    event_id=row[1],
                    name=row[2])
            for row in result] if result is not None else []


class Bet:
    def __init__(self, bet_id: int, outcome_id: int, event_id: int, player_id: int, display_name: str, amount: int):
        self.bet_id = bet_id
        self.outcome_id = outcome_id
        self.event_id = event_id
        self.player_id = player_id
        self.display_name = display_name
        self.amount = amount


def bet_from_id(bet_id: int) -> Bet:
    global EVENTS
    c = EVENTS.cursor()
    c.execute("SELECT bet_id, outcome_id, event_id, player_id, display_name, amount "
              "FROM bets WHERE bet_id = ?", (bet_id,))
    result = c.fetchone()
    return Bet(bet_id=result[0],
               outcome_id=result[1],
               event_id=result[2],
               player_id=result[3],
               display_name=result[4],
               amount=result[5]) if result is not None else None


def format_bet(bet: Bet) -> str:
    return f"{bet.display_name} ({bet.amount})"


def get_bets(outcome_id: int) -> list[Bet]:
    global EVENTS
    c = EVENTS.cursor()
    c.execute("SELECT bet_id, outcome_id, event_id, player_id, display_name, amount "
              "FROM bets WHERE outcome_id = ? "
              "ORDER BY bet_id", (outcome_id,))
    result = c.fetchall()
    return [Bet(bet_id=row[0],
                outcome_id=row[1],
                event_id=row[2],
                player_id=row[3],
                display_name=row[4],
                amount=row[5])
            for row in result] if result is not None else []


def format_outcome(outcome: Outcome) -> str:
    return "; ".join([format_bet(bet) for bet in get_bets(outcome.outcome_id)])


def create_embed(event_id: int) -> discord.Embed:
    event = event_from_id(event_id)
    embed = discord.Embed(title=event.name,
                          description="Bets for Ulduar",
                          color=0xFF5733)

    outcomes = get_outcomes(event_id)
    for outcome in outcomes:
        embed.add_field(name=outcome.name,
                        value=format_outcome(outcome),
                        inline=True)

    embed.set_author(name=event.author,
                     # url="https://discord.com/1",
                     icon_url="https://cdn.discordapp.com/app-icons/1082679337855226016/74d03e19ceff7789ab0c6828c3346558.png?size=64")

    pot = event.get_pot()
    embed.set_footer(text=f"Total pot: {pot}")

    return embed


def add_ulduar_event(author: str, name: str, channel: int) -> discord.Embed:
    """
    Add an Ulduar event to the database
    :param author: Who created the event
    :param name: Title for the event
    :param channel: Channel id to post
    :return: Embed object to be sent to the channel
    """
    global EVENTS
    EVENTS.execute("INSERT INTO events(name, author, channel_id) "
                   "VALUES(?, ?, ?)",
                   (name, author, channel,))
    EVENTS.commit()

    event_id = EVENTS.execute("SELECT last_insert_rowid()").fetchone()[0]

    for boss in [":fire: Flame Leviathan",
                 ":hammer: Ignis",
                 ":dragon_face: Razorscale",
                 ":recycle: XT-002",
                 ":blue_circle: Assembly of Iron",
                 "Kologarn",
                 ":cat: Auriaya",
                 ":fire_engine: Mimiron",
                 ":snowflake: Hodir",
                 ":cloud_lightning: Thorim",
                 ":sunflower: Freya",
                 ":squid: Vezax"]:
        EVENTS.execute("INSERT INTO outcomes(event_id, name) VALUES(?, ?)", (event_id, boss,))

    EVENTS.commit()
    return create_embed(event_id)
