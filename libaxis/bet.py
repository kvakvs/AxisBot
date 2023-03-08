import logging
from typing import Optional

from libaxis import players, db
from libaxis.conf import guild_conf
from libaxis.outcome import outcome_from_id

DATABASE = db.DB


class Bet:
    def __init__(self, bet_id: int, outcome_id: int, event_id: int, player_id: int, amount: int):
        self.bet_id = bet_id
        self.outcome_id = outcome_id
        self.event_id = event_id
        self.player_id = player_id
        self.amount = amount


def bet_from_id(bet_id: int) -> Bet:
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT bet_id, outcome_id, event_id, player_id, amount "
              "FROM bets WHERE bet_id = ?", (bet_id,))
    result = c.fetchone()
    return Bet(bet_id=result[0],
               outcome_id=result[1],
               event_id=result[2],
               player_id=result[3],
               amount=result[4]) if result is not None else None


def format_bet(bet: Bet) -> str:
    display_name = players.get_display_name(player_id=bet.player_id)
    return f"{display_name} ({bet.amount})"


def get_bets(outcome_id: int) -> list[Bet]:
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT bet_id, outcome_id, event_id, player_id, amount "
              "FROM bets WHERE outcome_id = ? "
              "ORDER BY bet_id", (outcome_id,))
    result = c.fetchall()
    return [Bet(bet_id=row[0],
                outcome_id=row[1],
                event_id=row[2],
                player_id=row[3],
                amount=row[4])
            for row in result] if result is not None else []


def find_bet(event_id: int, player_id: int) -> Optional[int]:
    """ Return bet id for this event and player, or None if no bet was placed """
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT outcome_id FROM bets WHERE event_id = ? AND player_id = ?",
              (event_id, player_id,))
    result = c.fetchone()
    return result if result is not None else None


def find_outcome_bet(event_id: int, outcome_id: int) -> Optional[int]:
    """ Return bet id for this event and outcome, or None if no bet was placed """
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT bet_id FROM bets WHERE event_id = ? AND outcome_id = ?",
              (event_id, outcome_id,))
    result = c.fetchone()
    return result if result is not None else None


def bet_on_outcome(event_id: int, outcome_id: int, player_id: int, display_name: str, gold: int) -> Optional[str]:
    wallet = players.get_balance(player_id=player_id)
    if wallet < gold:
        return f"You do not have {guild_conf['bet_amount']}g available in your wallet, " \
               "ask an officer to top you up with a /wallet command"

    if find_bet(event_id=event_id, player_id=player_id) is not None:
        return "You already have placed a bet on this event"
    if find_outcome_bet(event_id=event_id, outcome_id=outcome_id) is not None:
        return "Someone already has placed a bet on this outcome"

    outcome = outcome_from_id(outcome_id)

    logging.info(f"Player {player_id} ({display_name}) bets {gold} on id={outcome_id} ({outcome.name})")
    players.add_balance(player_id=player_id, gold=-gold)

    global DATABASE
    DATABASE.execute("INSERT OR IGNORE INTO bets(outcome_id, event_id, player_id, amount) "
                   "VALUES(?, ?, ?, 0)",
                     (outcome_id, event_id, player_id,))
    DATABASE.execute("UPDATE bets SET amount = amount + ? WHERE outcome_id = ? AND player_id = ?",
                     (gold, outcome_id, player_id,))
    DATABASE.commit()

    return None  # no error
