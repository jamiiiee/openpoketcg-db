import requests
import os

from bs4 import BeautifulSoup
from pathlib import Path


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TCG_RELEASES_URL = "https://bulbapedia.bulbagarden.net/wiki/Template:TCG_Releases"
HTML_DIR = Path("html")


def find_series_tables():
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


def get_rebuild_links(tables, eras):
    downloaded_sets = {
        os.path.splitext(f)[0] for f in os.listdir(HTML_DIR) if f.endswith(".html")
    }
    return [
        (a["href"], a.text.strip().replace("/", " "))
        for table in tables
        for a in table.find_all("a", href=True)
        if any(th.text.strip() in eras for th in table.find_all("th"))
        if a.text.strip().replace("/", " ") not in downloaded_sets
    ]


def get_updated_links(tables, eras):
    return [
        (a["href"], a.text.strip().replace("/", " "))
        for table in tables
        if any(th.text.strip() in eras for th in table.find_all("th"))
        for a in table.find_all("a", href=True)[-4:]
    ]


def download_html(links):
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        for link, title in links:
            url = f"https://bulbapedia.bulbagarden.net{link}"
            filename = HTML_DIR / f"{title}.html"

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

    tables = find_series_tables()

    if rebuild:
        links = get_rebuild_links(tables, eras)
    else:
        links = get_updated_links(tables, eras)

    download_html(links)
