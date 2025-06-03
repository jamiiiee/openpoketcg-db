from scraper.db import db_cursor


def get_ongoing_era_names():
    with db_cursor() as cur:
        cur.execute("SELECT name FROM eras WHERE ongoing = TRUE;")
        return [row[0] for row in cur.fetchall()]


# download(ongoing_eras)
# data = scraper()
# update sets and cards
