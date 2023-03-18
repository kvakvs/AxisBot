import logging
from typing import Optional

from libaxis import item_cache, db

DATABASE = db.DB
logger = logging.getLogger('crafting')


class Craftable:
    def __init__(self, player_id: int, item_id: int):
        self.player_id = player_id
        self.item_id = item_id
        self.item = None  # type: Optional[item_cache.CachedItem]

    def load_item(self):
        self.item = item_cache.find_item(self.item_id)


def learn_craft(player_id: int, item_id: int) -> Optional[item_cache.CachedItem]:
    try:
        item_info = item_cache.find_item(item_id)
        c = DATABASE.cursor()
        c.execute("INSERT INTO craftables (player_id, item_id) VALUES (?, ?)", (player_id, item_id))
        DATABASE.commit()
        return item_info

    except Exception as e:
        logger.error(str(e))
        return None


def forget_craft(player_id: int, item_id: int):
    c = DATABASE.cursor()
    c.execute("DELETE FROM craftables WHERE player_id = ? AND item_id = ?", (player_id, item_id))
    DATABASE.commit()


def find_all_crafts(text: str, subclass: Optional[str]) -> dict[int, list[Craftable]]:
    c = DATABASE.cursor()
    c.execute("SELECT craftables.player_id, craftables.item_id FROM craftables "
              "LEFT JOIN item_cache ON craftables.item_id = item_cache.item_id "
              "WHERE item_cache.wowhead_stripped LIKE ? AND item_cache.subclass LIKE ?",
              (f"%{text}%", subclass if subclass is not None else "%"))
    rows = c.fetchall()
    craftables = list(map(lambda row: Craftable(player_id=row[0], item_id=row[1]), rows))

    result = {}
    for craftable in craftables:
        if craftable.item_id not in result:
            craftable.load_item()  # only load first item in the craftables
            result[craftable.item_id] = [craftable]
        else:
            result[craftable.item_id].append(craftable)

    return result
