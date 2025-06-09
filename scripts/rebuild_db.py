from scraper.download import update_html
from scraper.db import db_cursor
from scraper.pipeline import get_cards, get_era_map, get_language_map, insert_cards
from scraper.storage import retrieve_html, update_html_zip, clean_html
from scraper.scrape_html import scrape_html

SQL_TRUNCATE = """
TRUNCATE TABLE cards, sets RESTART IDENTITY CASCADE;
"""

SQL_INSERT_SETS = """
INSERT INTO sets (id, name, release_date, type, era_id)
VALUES (%(id)s, %(name)s, %(release_date)s, %(type)s, %(era_id)s)
ON CONFLICT (id) DO NOTHING;
"""


def truncate_tables():
    with db_cursor() as cur:
        cur.execute(SQL_TRUNCATE)


def insert_sets(sets):
    with db_cursor() as cur:
        cur.executemany(SQL_INSERT_SETS, sets)


language_map = get_language_map()
era_map = get_era_map()
era_list = list(era_map.keys())

retrieve_html()
update_html(rebuild=True, eras=era_list)

sets = scrape_html(language_map, era_map)
cards = get_cards(sets)

truncate_tables()
insert_sets(sets)
insert_cards(cards)

update_html_zip()
clean_html()
