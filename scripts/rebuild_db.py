from scraper.download import update_html
from scraper.db import db_cursor

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


update_html(rebuild=True, eras=get_era_names())

# data = scraper()
# set sets and cards
