import logging

from libaxis import db
from lxml import html, etree
import requests

DATABASE = db.DB
logger = logging.getLogger('item_cache')


class CachedItem:
    def __init__(self, item_id: int, item_name: str, wowhead_xml: str, wowhead_stripped: str, link: str,
                 subclass: str):
        self.item_id = item_id
        self.item_name = item_name
        self.link = link
        self.subclass = subclass
        self.wowhead_stripped = wowhead_stripped
        self.wowhead_xml = wowhead_xml

    def __str__(self) -> str:
        return f"Cached(name={self.item_name}, id={self.item_id}, subclass={self.subclass})"

    def save(self):
        c = DATABASE.cursor()
        c.execute("INSERT INTO item_cache (item_id, item_name, wowhead_xml, wowhead_stripped, link, subclass) "
                  "VALUES (?, ?, ?, ?, ?, ?)",
                  (self.item_id, self.item_name, self.wowhead_xml, self.wowhead_stripped, self.link, self.subclass))
        DATABASE.commit()


def find_item_in_database(item_id: int):
    c = DATABASE.cursor()
    c.execute("SELECT item_id, item_name, wowhead_xml, wowhead_stripped, link, subclass FROM item_cache "
              "WHERE item_id = ?", (item_id,))
    result = c.fetchone()
    return CachedItem(item_id=result[0],
                      item_name=result[1],
                      wowhead_xml=result[2],
                      wowhead_stripped=result[3],
                      link=result[4],
                      subclass=result[5]) if result is not None else None


def strip_xml(text: str) -> str:
    tree = html.fromstring(f"<html><body>{text}</body></html>")
    notags = etree.tostring(tree, encoding='utf8', method='text')
    return notags.decode('utf8')


def find_item_on_wowhead(item_id: int):
    logger.info(f"Fetch from wowhead: item={item_id}")

    page = requests.get(f"https://www.wowhead.com/wotlk/item={item_id}&xml")
    tree = etree.fromstring(page.content)
    # Tree contains:
    # wowhead/item/...
    name = tree.xpath('/wowhead/item/name/text()')[0]
    subclass = tree.xpath('/wowhead/item/subclass/text()')[0]
    link = tree.xpath('/wowhead/item/link/text()')[0]
    xml = tree.xpath('/wowhead/item/htmlTooltip[1]/text()')[0].replace("<br>", "<br/>")

    item_info = CachedItem(item_id=item_id,
                           item_name=name,
                           wowhead_xml=xml,
                           wowhead_stripped=strip_xml(xml),
                           link=link,
                           subclass=subclass)
    item_info.save()
    return item_info


def find_item(item_id: int):
    db_item = find_item_in_database(item_id)
    return db_item if db_item is not None else find_item_on_wowhead(item_id)
