import os
from parse_pages import find_release_date
from parse_tables import parse_tables


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


def _filter_data(rows):
    if len(rows) == 0:
        return []

    print(rows)

    headers = list(rows[0].keys())
    non_empty_columns = []

    for header in headers:
        values = [row[header] for row in rows if row[header] not in ("-", "")]
        if len(set(values)) > 1:
            non_empty_columns.append(header)

    filtered_rows = [{key: row[key] for key in non_empty_columns} for row in rows]

    return filtered_rows


def scrape_html(language="English"):
    file_paths = _get_set_file_paths()
    for file_path, era_name, set_name in file_paths[:5]:
        release_date, parsed_tables, set_type = _process_set_file(
            file_path, language, set_name
        )
        filtered_tables = [_filter_data(table) for table in parsed_tables]
        print(f"Era: {era_name}, Set: {set_name}, Release Date: {release_date}")
        print(filtered_tables)
        print(set_type)


scrape_html()
