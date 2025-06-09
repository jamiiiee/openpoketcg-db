from scraper.download import update_html
from scraper.db import db_cursor
from scraper.scrape_html import scrape_html
from scraper.storage import clean_html

SQL_SELECT_ONGOING_ERAS = """
SELECT name FROM eras WHERE ongoing = TRUE;
"""

SQL_SELECT_LANGUAGES = """
SELECT id, name FROM languages;
"""

SQL_SELECT_ERAS = """
SELECT id, name, language_id FROM eras;
"""

SQL_DELETE_CARDS_FOR_SETS = """
DELETE FROM cards
WHERE set_id = ANY(%s);
"""

SQL_INSERT_SETS = """
INSERT INTO sets (id, name, release_date, type, era_id)
VALUES (%(id)s, %(name)s, %(release_date)s, %(type)s, %(era_id)s)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    release_date = EXCLUDED.release_date,
    type = EXCLUDED.type,
    era_id = EXCLUDED.era_id;
"""

SQL_INSERT_CARDS = """
INSERT INTO cards (
    set_number, mark, name, type, rarity,
    promotion, quantity, set_id
)
VALUES (
    %(set_number)s, %(mark)s, %(name)s, %(type)s, %(rarity)s,
    %(promotion)s, %(quantity)s, %(set_id)s
)
ON CONFLICT (set_id, set_number, name) DO NOTHING;
"""

REQUIRED_FIELDS = [
    "set_id",
    "set_number",
    "mark",
    "name",
    "type",
    "rarity",
    "promotion",
    "quantity",
]


def get_language_map():
    with db_cursor() as cur:
        cur.execute(SQL_SELECT_LANGUAGES)
        return {id: name for id, name in cur.fetchall()}


def get_era_map():
    with db_cursor() as cur:
        cur.execute(SQL_SELECT_ERAS)
        return {name: (id, language_id) for id, name, language_id in cur.fetchall()}


def get_ongoing_era_names():
    with db_cursor() as cur:
        cur.execute(SQL_SELECT_ONGOING_ERAS)
        return [row[0] for row in cur.fetchall()]


def get_cards(sets):
    return [
        {
            **{field: card.get(field, None) for field in REQUIRED_FIELDS},
            "set_id": set["id"],
        }
        for set in sets
        for table in set["tables"]
        for card in table
    ]


def delete_cards(set_ids):
    with db_cursor() as cur:
        cur.execute(SQL_DELETE_CARDS_FOR_SETS, (set_ids,))


def insert_sets(sets):
    with db_cursor() as cur:
        cur.executemany(SQL_INSERT_SETS, sets)


def insert_cards(cards):
    with db_cursor() as cur:
        cur.executemany(SQL_INSERT_CARDS, cards)


language_map = get_language_map()
era_map = get_era_map()
ongoing_era_list = get_ongoing_era_names()

update_html(rebuild=False, eras=ongoing_era_list)

sets = scrape_html(language_map, era_map)
set_ids = [set["id"] for set in sets]
cards = get_cards(sets)

delete_cards(set_ids)
insert_sets(sets)
insert_cards(cards)

clean_html()
