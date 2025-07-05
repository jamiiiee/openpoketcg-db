from scraper.download import update_html
from scraper.db import db_cursor
from scraper.pipeline import get_cards, get_era_map, get_language_map, insert_cards
from scraper.scrape_html import scrape_html
from scraper.storage import clean_html

SQL_SELECT_ONGOING_ERAS = """
SELECT name FROM eras WHERE ongoing = TRUE;
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


def get_ongoing_era_names():
    with db_cursor() as cur:
        cur.execute(SQL_SELECT_ONGOING_ERAS)
        return [row[0] for row in cur.fetchall()]


def delete_cards(set_ids):
    with db_cursor() as cur:
        cur.execute(SQL_DELETE_CARDS_FOR_SETS, (set_ids,))


def insert_sets(sets):
    with db_cursor() as cur:
        cur.executemany(SQL_INSERT_SETS, sets)


print("Starting database update")
language_map = get_language_map()
era_map = get_era_map()
ongoing_era_list = get_ongoing_era_names()

print("Downloading recent HTML for ongoing eras")
update_html(rebuild=False, eras=ongoing_era_list)

print("Scraping HTML files")
sets = scrape_html(language_map, era_map)
set_ids = [set["id"] for set in sets]
cards = get_cards(sets)

print("Updating database")
delete_cards(set_ids)
insert_sets(sets)
insert_cards(cards)

clean_html()

print("Database update completed successfully")
