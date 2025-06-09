from scraper.download import update_html
from scraper.db import db_cursor
from scraper.storage import retrieve_html, update_html_zip, clean_html
from scraper.scrape_html import scrape_html

SQL_TRUNCATE = """
TRUNCATE TABLE cards, sets RESTART IDENTITY CASCADE;
"""

SQL_SELECT_LANGUAGES = """
SELECT id, name FROM languages;
"""

SQL_SELECT_ERAS = """
SELECT id, name, language_id FROM eras;
"""

SQL_INSERT_SETS = """
INSERT INTO sets (id, name, release_date, type, era_id)
VALUES (%(id)s, %(name)s, %(release_date)s, %(type)s, %(era_id)s)
ON CONFLICT (id) DO NOTHING;
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


def truncate_tables():
    with db_cursor() as cur:
        cur.execute(SQL_TRUNCATE)


def get_language_map():
    with db_cursor() as cur:
        cur.execute(SQL_SELECT_LANGUAGES)
        return {id: name for id, name in cur.fetchall()}


def get_era_map():
    with db_cursor() as cur:
        cur.execute(SQL_SELECT_ERAS)
        return {name: (id, language_id) for id, name, language_id in cur.fetchall()}


def insert_sets(sets):
    with db_cursor() as cur:
        cur.executemany(SQL_INSERT_SETS, sets)


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


def insert_cards(cards):
    with db_cursor() as cur:
        cur.executemany(SQL_INSERT_CARDS, cards)


language_map = get_language_map()
era_map = get_era_map()
era_list = list(era_map.keys())

retrieve_html()
update_html(rebuild=True, eras=era_list)
update_html_zip()

sets = scrape_html(language_map, era_map)
cards = get_cards(sets)

truncate_tables()
insert_sets(sets)
insert_cards(cards)

clean_html()
