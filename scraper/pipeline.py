from scraper.db import db_cursor


SQL_SELECT_LANGUAGES = """
SELECT id, name FROM languages;
"""

SQL_SELECT_ERAS = """
SELECT id, name, language_id FROM eras;
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
