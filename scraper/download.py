import requests
import time
import unicodedata

from bs4 import BeautifulSoup
from pathlib import Path


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TCG_RELEASES_URL = "https://bulbapedia.bulbagarden.net/wiki/Template:TCG_Releases"
HTML_DIR = Path("html")


def _normalise_name(name):
    return unicodedata.normalize("NFKC", name).replace("\u00a0", " ").strip()


def _find_series_tables():
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        try:
            response = session.get(TCG_RELEASES_URL)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching series tables: {e}")
            return []

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find_all("table", {"width": "100%"})


def _get_rebuild_links(tables, eras):
    downloaded_sets = {_normalise_name(f.stem) for f in HTML_DIR.rglob("*.html")}

    return [
        (a["href"], a.text.strip().replace("/", " "), th.text.strip())
        for table in tables
        for th in table.find_all("th")
        if _normalise_name(th.text.strip()) in eras
        for a in (table.find("td")).find_all("a", href=True)
        if _normalise_name(a.text.strip().replace("/", " ")) not in downloaded_sets
    ]


def _get_updated_links(tables, eras):
    return [
        (a["href"], a.text.strip().replace("/", " "), th.text.strip())
        for table in tables
        for th in table.find_all("th")
        if _normalise_name(th.text.strip()) in eras
        for a in (table.find("td")).find_all("a", href=True)[-4:]
    ]


def _download_html(links):
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        for link, title, era in links:
            time.sleep(4)
            url = f"https://bulbapedia.bulbagarden.net{link}"
            era_dir = HTML_DIR / _normalise_name(era)
            era_dir.mkdir(parents=True, exist_ok=True)
            filename = era_dir / f"{title}.html"

            try:
                response = session.get(url)
                response.raise_for_status()
            except Exception as e:
                print(f"Error downloading {url}: {e}")

            with open(filename, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Downloaded: {filename}")


def update_html(rebuild, eras):
    if not HTML_DIR.exists():
        HTML_DIR.mkdir(parents=True)

    tables = _find_series_tables()

    if rebuild:
        links = _get_rebuild_links(tables, eras)
    else:
        links = _get_updated_links(tables, eras)

    _download_html(links)
