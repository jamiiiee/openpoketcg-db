import os
from scraper.parse_pages import find_release_date
from scraper.parse_tables import parse_tables


def _get_set_file_paths():
    return [
        (
            os.path.join("html", era_folder, set_file),
            era_folder,
            os.path.splitext(set_file)[0],
        )
        for era_folder in os.listdir("html")
        if os.path.isdir(os.path.join("html", era_folder))
        for set_file in os.listdir(os.path.join("html", era_folder))
        if set_file.endswith(".html")
    ]


def _process_set_file(file_path, language, set_name):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            html = file.read()

        release_date = find_release_date(html, language)
        parsed_tables, set_type = parse_tables(html, set_name)
        return release_date, parsed_tables, set_type

    except Exception as e:
        print(f"Could not read {file_path}: {e}")


def scrape_html(language_map, era_map):
    file_paths = _get_set_file_paths()
    results = []
    for file_path, era_name, set_name in file_paths:
        era_id, language_id = era_map[era_name]
        release_date, parsed_tables, set_type = _process_set_file(
            file_path, language_map[language_id], set_name
        )
        results.append(
            {
                "id": f"{era_id}-{set_name}",
                "era_id": era_id,
                "name": set_name,
                "release_date": release_date,
                "type": set_type,
                "tables": parsed_tables,
            }
        )

    return results
