from scraper.download import update_html
from scraper.db import db_cursor
from scraper.storage import retrieve_html, update_html_zip, clean_html

SQL_SELECT_ONGOING_ERAS = """
SELECT name FROM eras WHERE ongoing = TRUE;
"""


def get_ongoing_era_names():
    with db_cursor() as cur:
        cur.execute(SQL_SELECT_ONGOING_ERAS)
        return [row[0] for row in cur.fetchall()]


retrieve_html()
update_html(rebuild=False, eras=get_ongoing_era_names())
update_html_zip()

# data = scraper()
# update sets and cards

clean_html()
