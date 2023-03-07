import logging
import sqlite3

logger = logging.getLogger('main')


def init_db():
    conn = sqlite3.connect("axisbot.db")
    # c = conn.cursor()
    # c.execute(open("sql/players.sql", encoding='utf-8-sig').read())
    # conn.commit()
    return conn


PLAYERS = init_db()


def ensure_exists(player_id: int, discord_name: str, display_name: str):
    global PLAYERS
    PLAYERS.execute("INSERT OR IGNORE INTO players(id, discord_name, display_name, balance) "
                    "VALUES(?, ?, ?, 0)",
                    (player_id, discord_name, display_name,))
    PLAYERS.commit()
    logger.info(f"Player {discord_name} ({display_name}) added to database")


def get_balance(player_id: int) -> int:
    """
    Get player balance (wow gold)
    :param player_id: Member integer id
    :return: The wow gold that player stored in the guild bank
    """
    global PLAYERS
    c = PLAYERS.cursor()
    c.execute("SELECT balance FROM players WHERE id = ?", (player_id,))
    result = c.fetchone()
    return result[0] if result is not None else 0


def add_balance(player_id: int, gold: int):
    """ Increase player balance (deposited into guild bank)
    """
    if gold < 0:
        logger.info(f"Removing {-gold} gold from player {player_id}")
    else:
        logger.info(f"Adding {gold} gold to player {player_id}")

    global PLAYERS
    c = PLAYERS.cursor()
    c.execute("UPDATE players SET balance = balance + (?) WHERE id = ?", (gold, player_id))
    PLAYERS.commit()
