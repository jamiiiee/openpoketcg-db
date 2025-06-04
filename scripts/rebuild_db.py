from scraper.download import update_html
from scraper.db import db_cursor
from scraper.storage import retrieve_html, update_html_zip, clean_html

SQL_TRUNCATE = """
TRUNCATE TABLE cards, sets RESTART IDENTITY CASCADE;
"""

SQL_SELECT_ERA_NAMES = """
SELECT name FROM eras;
"""


def truncate_tables():
    with db_cursor() as cur:
        cur.execute(SQL_TRUNCATE)


def get_era_names():
    with db_cursor() as cur:
        cur.execute(SQL_SELECT_ERA_NAMES)
        return [row[0] for row in cur.fetchall()]


retrieve_html()
truncate_tables()
update_html(rebuild=True, eras=get_era_names())
update_html_zip()

# data = scraper()
# set sets and cards

clean_html()
