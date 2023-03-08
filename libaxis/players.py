import logging

from libaxis import db

logger = logging.getLogger('main')

DATABASE = db.DB


def ensure_exists(player_id: int, discord_name: str, display_name: str):
    global DATABASE
    DATABASE.execute("INSERT OR IGNORE INTO players(player_id, discord_name, display_name, balance) "
                     "VALUES(?, ?, ?, 0)",
                     (player_id, discord_name, display_name,))
    DATABASE.commit()
    logger.info(f"Player {discord_name} ({display_name}) added to database")


def get_balance(player_id: int) -> int:
    """
    Get player balance (wow gold)
    :param player_id: Member integer id
    :return: The wow gold that player stored in the guild bank
    """
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT balance FROM players WHERE player_id = ?", (player_id,))
    result = c.fetchone()
    return result[0] if result is not None else 0


def add_balance(player_id: int, gold: int):
    """ Increase player balance (deposited into guild bank)
    """
    if gold < 0:
        logger.info(f"Removing {-gold} gold from player {player_id}")
    else:
        logger.info(f"Adding {gold} gold to player {player_id}")

    global DATABASE
    c = DATABASE.cursor()
    c.execute("UPDATE players SET balance = balance + (?) WHERE player_id = ?", (gold, player_id))
    DATABASE.commit()


def get_display_name(player_id: int) -> str:
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT display_name FROM players WHERE player_id = ?", (player_id,))
    result = c.fetchone()
    return result[0] if result is not None and result[0] is not None else None
