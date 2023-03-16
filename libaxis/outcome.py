from typing import Union

from libaxis import db

DATABASE = db.DB


class Outcome:
    def __init__(self, outcome_id: int, event_id: int, name: str, success: Union[bool, int]):
        self.success = success or success == 1
        self.outcome_id = outcome_id
        self.event_id = event_id
        self.name = name

    def cut_first_word(self):
        """ Return everything AFTER the first word, which should be all text after :emoji: """
        return self.name.split(sep=" ", maxsplit=1)[1]

    def get_first_word(self):
        return self.name.split(sep=" ", maxsplit=1)[0]

    def is_available(self):
        """
        Check outcome availability for bet placement
        :return: True if the outcome doesn't have a bet placed on it
        """
        from libaxis import bet
        return bet.find_outcome_bet(self.event_id, self.outcome_id) is None


def outcome_from_id(outcome_id: int) -> Outcome:
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT outcome_id, event_id, name, success "
              "FROM outcomes WHERE outcome_id = ?", (outcome_id,))
    result = c.fetchone()
    return Outcome(outcome_id=result[0],
                   event_id=result[1],
                   name=result[2],
                   success=result[3]) if result is not None else None


def get_outcomes(event_id: int) -> list[Outcome]:
    global DATABASE
    c = DATABASE.cursor()
    c.execute("SELECT outcome_id, event_id, name, success "
              "FROM outcomes WHERE event_id = ? ORDER BY outcome_id", (event_id,))
    result = c.fetchall()
    return [Outcome(outcome_id=row[0],
                    event_id=row[1],
                    name=row[2],
                    success=row[3])
            for row in result] if result is not None else []


def format_outcome(outcome: Outcome) -> str:
    from libaxis.bet import format_bet, get_bets
    return "; ".join([format_bet(bet) for bet in get_bets(outcome.outcome_id)])


def toggle_first_matching_outcome(event_id: int, search_str: str):
    """
    Toggle the matching outcomes in the event, by a name substring
    :param event_id: Event ID
    :param search_str: Outcome search substring
    """
    global DATABASE
    c = DATABASE.cursor()
    c.execute("UPDATE outcomes SET success = NOT success WHERE event_id = ? AND name LIKE ? ",
              (event_id, f"%{search_str}%",))
