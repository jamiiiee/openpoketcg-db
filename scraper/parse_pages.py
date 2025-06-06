import re

from bs4 import BeautifulSoup

year_pattern = re.compile(r"\d{4}")
full_date_pattern = re.compile(r".*?\d{4}")


def find_release_date(html, language):
    soup = BeautifulSoup(html, "html.parser")

    release_pattern = re.compile(r"Release\s+date|Release\s+period", re.IGNORECASE)

    for th in soup.find_all("th"):
        text = th.get_text(strip=True)
        if not text:
            continue

        match = release_pattern.search(text)
        if not match:
            continue

        td = th.find_next_sibling("td")
        if not td:
            continue

        text = td.get_text(strip=True)
        if not text:
            continue

        if ":" not in text and year_pattern.search(text):
            if match := full_date_pattern.search(text):
                return match.group(0).strip()

        language_dates = _extract_language_dates(text)

        if language in language_dates:
            return language_dates[language]
        elif language_dates:
            return next(iter(language_dates.values()))

    return None


def _extract_language_dates(text):
    language_section_pattern = re.compile(r"([A-Za-z\s]+:)")

    language_dates = {}
    sections = language_section_pattern.split(text)

    for i in range(1, len(sections), 2):
        if i + 1 >= len(sections):
            break

        lang = sections[i][:-1].strip()
        date = sections[i + 1].strip()

        if year_pattern.search(date):
            if match := full_date_pattern.search(date):
                language_dates[lang] = match.group(0).strip()

    return language_dates
