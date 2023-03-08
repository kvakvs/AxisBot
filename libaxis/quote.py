from typing import Optional

import discord

from libaxis import db

DATABASE = db.DB


class Quote:
    def __init__(self, key: str, player_id: int, text: str):
        self.key = key
        self.player_id = player_id
        self.text = text

    def format(self) -> str:
        return self.text


def get_quote(key: str) -> Optional[Quote]:
    """
    Get a quote from the database
    :param key: Short string key
    :return: Quote object or None
    """
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT quote_key, player_id, quote FROM quotes WHERE quote_key = ?", (key,))
    result = c.fetchone()
    return Quote(key=result[0],
                 player_id=result[1],
                 text=result[2]) if result is not None else None


def learn_quote(player_id: int, quote_key: str, quote_text: str):
    """
    Store a quote in the database
    :param quote_key: Short string key
    :param player_id: Who taught the quote
    :param quote_text: The text
    """
    forget_quote(player_id, quote_key)

    global DATABASE
    c = DATABASE.cursor()
    c.execute("INSERT INTO quotes (player_id, quote_key, quote) VALUES (?, ?, ?)",
              (player_id, quote_key, quote_text,))
    DATABASE.commit()


def forget_quote(player_id: int, quote_key: str):
    """
    Remove a quote from the database
    :param player_id: Who taught the quote
    :param quote_key: Short string key
    """
    global DATABASE
    c = DATABASE.cursor()
    c.execute("DELETE FROM quotes WHERE player_id = ? AND quote_key = ?",
              (player_id, quote_key,))
    DATABASE.commit()


def get_user_quote_keys(player_id: int) -> list[str]:
    """
    Get all quote keys for a user
    :param player_id: Who taught the quote
    :return: List of quote keys
    """
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT quote_key FROM quotes WHERE player_id = ? ORDER BY quote_key", (player_id,))
    result = c.fetchall()
    return [row[0] for row in result] if result is not None else []


def get_other_users_quote_keys(player_id: int) -> list[str]:
    """
    Get all quote keys not owned by the user
    :return: List of quote keys
    """
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT quote_key FROM quotes WHERE player_id <> ? ORDER BY quote_key", (player_id,))
    result = c.fetchall()
    return [row[0] for row in result] if result is not None else []
