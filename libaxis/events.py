from typing import Optional, Tuple

import discord

from libaxis import db
from libaxis.conf import guild_conf
from libaxis.outcome import get_outcomes, format_outcome

DATABASE = db.DB
ICON_URL = "https://cdn.discordapp.com/app-icons/1082679337855226016/1aafcc8246cf43dd914ae5d5cf5e93c3.png?size=64"


class Event:
    """
    Describes a weekly gambling event.
    Create only after the previous week has been concluded.
    """

    def __init__(self, event_id: int, name: str, author: str, channel_id: int, is_locked: bool,
                 embed_id: Optional[int] = None):
        self.author = author
        self.channel_id = channel_id
        self.embed_id = embed_id
        self.event_id = event_id
        self.is_locked = is_locked
        self.name = name

    def get_pot(self) -> int:
        global DATABASE
        c = DATABASE.cursor()
        c.execute("SELECT SUM(amount) FROM bets WHERE event_id = ?", (self.event_id,))
        result = c.fetchone()
        return result[0] if result[0] is not None else 0


def event_from_id(event_id: int) -> Event:
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT event_id, name, author, channel_id, embed_id, is_locked "
              "FROM events WHERE event_id = ?", (event_id,))
    result = c.fetchone()
    return Event(event_id=result[0],
                 name=result[1],
                 author=result[2],
                 channel_id=result[3],
                 embed_id=result[4],
                 is_locked=result[5]) if result is not None else None


def create_embed(event_id: int) -> discord.Embed:
    event = event_from_id(event_id)

    descriptions = ["Gamble for Val'anyr fragments in Ulduar this week."]
    color = 0xFF5733
    if event.is_locked:
        descriptions.append(":lock: This event is locked. No more bets can be placed.")
        color = 0xFF0000  # make it red

    embed = discord.Embed(title=f"{event.name} [event_id={event_id}]",
                          url="https://github.com/kvakvs/AxisBot/blob/master/README.md",
                          description=" ".join(descriptions),
                          color=color)

    outcomes = get_outcomes(event_id)
    for outcome in outcomes:
        embed.add_field(name=outcome.name,
                        value=format_outcome(outcome),
                        inline=True)

    success_outcomes = filter(lambda o: o.success == 1, outcomes)
    success_outcomes_str = "; ".join([o.cut_first_word() for o in success_outcomes]) or "Not just yet?"

    embed.set_author(name=event.author,
                     # url="https://discord.com/1",
                     icon_url=ICON_URL)

    pot = event.get_pot()
    embed.set_footer(text=f"Total in the pot: {pot}g\n"
                          f"Success outcomes: {success_outcomes_str}\n"
                          f"To place a bet: {guild_conf['bet_amount']}g\n"
                          "\n"
                          f"Type `/bet` and hit Enter to place a bet.\n"
                          f"Officers can update your betting wallet when you deposit.\n")

    return embed


def add_ulduar_event(author: str, name: str, channel: int) -> Tuple[int, discord.Embed]:
    """
    Add an Ulduar event to the database
    :param author: Who created the event
    :param name: Title for the event
    :param channel: Channel id to post
    :return: Embed object to be sent to the channel
    """
    global DATABASE
    DATABASE.execute("INSERT INTO events(name, author, channel_id) "
                     "VALUES(?, ?, ?)",
                     (name, author, channel,))
    DATABASE.commit()

    event_id = DATABASE.execute("SELECT last_insert_rowid()").fetchone()[0]

    for boss in [":fire: Flame Leviathan",
                 ":hammer: Ignis",
                 ":dragon_face: Razorscale",
                 ":recycle: XT-002",
                 ":blue_circle: Assembly of Iron",
                 ":hand_splayed: Kologarn",
                 ":cat: Auriaya",
                 ":fire_engine: Mimiron",
                 ":snowflake: Hodir",
                 ":cloud_lightning: Thorim",
                 ":sunflower: Freya",
                 ":squid: Vezax",
                 ":star: Algalon"]:
        DATABASE.execute("INSERT INTO outcomes(event_id, name) VALUES(?, ?)", (event_id, boss,))

    DATABASE.commit()
    return event_id, create_embed(event_id)


def update_event_embed_id(event_id: int, embed_id: int):
    """ Having posted embed for the event, store its id. """
    global DATABASE
    DATABASE.execute("UPDATE events SET embed_id = ? WHERE event_id = ?", (embed_id, event_id,))
    DATABASE.commit()


async def update_event_embed(event_id: int, client: discord.Client):
    event = event_from_id(event_id)
    channel = client.get_channel(event.channel_id)
    msg = await channel.fetch_message(event.embed_id)
    await msg.edit(embed=create_embed(event_id))


async def bump_event(event_id: int, client: discord.Client):
    """
    Repost event id, and delete the one higher up
    """
    event = event_from_id(event_id)
    channel = client.get_channel(event.channel_id)
    try:
        msg = await channel.fetch_message(event.embed_id)
        await msg.delete(delay=1.0)
    except discord.NotFound:
        pass
    bumped = await channel.send(embed=create_embed(event_id))
    update_event_embed_id(event_id, bumped.id)


def find_latest_event():
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT event_id FROM events ORDER BY event_id DESC LIMIT 1")
    result = c.fetchone()
    return result[0] if result[0] is not None else None


def lock_event(event_id: int):
    global DATABASE
    DATABASE.execute("UPDATE events SET is_locked = 1 WHERE event_id = ?", (event_id,))
    DATABASE.commit()


def is_event_locked(event_id: int) -> bool:
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT is_locked FROM events WHERE event_id = ?", (event_id,))
    result = c.fetchone()
    return result[0] if result[0] is not None else False
