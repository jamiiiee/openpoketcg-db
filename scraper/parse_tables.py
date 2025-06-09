from bs4 import BeautifulSoup


REQUIRED_TABLE_KEYWORDS = {"set list", "card list", "deck list"}
REQUIRED_HEADER_KEYWORDS = {"no", "card", "type"}
HEADER_MAP = {
    "no.": "set_number",
    "number": "set_number",
    "no": "set_number",
    "mark": "mark",
    "card": "name",
    "card name": "name",
    "name": "name",
    "type": "type",
    "rarity": "rarity",
    "promotion": "promotion",
    "quantity": "quantity",
}
EMPTY_CELL_PLACEHOLDER = "-"


def _find_good_tables(soup):
    good_tables = []

    for table in soup.find_all("table", class_="roundy"):
        header = table.find_previous(["h2", "h3", "h4"])
        if not header:
            continue

        header_text = header.get_text().strip().lower()
        matched_keyword = next(
            (
                header.get_text().strip()
                for keyword in REQUIRED_TABLE_KEYWORDS
                if keyword in header_text
            ),
            None,
        )

        if not matched_keyword or len(table.find_all("tr")) < 2:
            continue

        good_tables.append((table, matched_keyword))

    return good_tables


def _find_header_row(table):
    for i, row in enumerate(table.find_all("tr")[:3]):
        cells = row.find_all(["th", "td"])
        cell_texts = [cell.get_text(strip=True).lower() for cell in cells]

        if all(
            any(keyword in text for text in cell_texts)
            for keyword in REQUIRED_HEADER_KEYWORDS
        ):
            return row, i

    return None, -1


def _extract_headers(header_row):
    headers = [
        HEADER_MAP[cell.get_text().strip().lower()]
        for cell in header_row.find_all(["th", "td"])
        if not (cell.get("style") and "display:none" in cell.get("style").lower())
        and cell.get_text().strip().lower() in HEADER_MAP
    ]

    return list(dict.fromkeys(headers))


def _process_cell(cell):
    text_parts = []

    def extract_text(node):
        if isinstance(node, str):
            if node.strip():
                text_parts.append(node.strip())
        elif node.name == "img" and node.get("alt"):
            text_parts.append(node.get("alt").strip())
        elif node.name == "br":
            return False
        elif hasattr(node, "children"):
            for child in node.children:
                if extract_text(child) is False:
                    return False
        return True

    extract_text(cell)
    return " ".join(text_parts) or EMPTY_CELL_PLACEHOLDER


def _is_valid_row(row_data, headers, seen_rows):
    if tuple(row_data) in seen_rows:
        return False

    if all(cell == EMPTY_CELL_PLACEHOLDER for cell in row_data):
        return False

    if len(row_data) == len(headers) and all(
        cell.lower() == header.lower() for cell, header in zip(row_data, headers)
    ):
        return False

    return True


def _parse_rows(table, header_row_index, headers):
    data_rows = []
    seen_rows = set()

    for row in table.find_all("tr")[header_row_index + 1 :]:
        cells = [
            cell
            for cell in row.find_all(["td", "th"])
            if not (cell.get("style") and "display:none" in cell.get("style").lower())
            and not cell.get("colspan")
        ]
        if not cells:
            continue

        row_data = [_process_cell(cell) for cell, _ in zip(cells, headers)]

        while len(row_data) < len(headers):
            row_data.append(EMPTY_CELL_PLACEHOLDER)

        if not _is_valid_row(row_data, headers, seen_rows):
            continue

        seen_rows.add(tuple(row_data))
        data_rows.append(row_data)

    return data_rows


def _is_duplicate_header_row(row, headers):
    return all(
        row[i].strip().lower() in HEADER_MAP
        and HEADER_MAP[row[i].strip().lower()] == headers[i]
        for i in range(len(headers))
    )


def parse_tables(html, set_name):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    good_tables = _find_good_tables(soup)

    if not good_tables:
        return results, None

    for table, list_type in good_tables:
        header_row, header_row_index = _find_header_row(table)
        if not header_row:
            continue

        headers = _extract_headers(header_row)
        if not headers:
            continue

        title = table.find_next("big").get_text().strip()
        if set_name not in title:
            continue

        data_rows = _parse_rows(table, header_row_index, headers)
        if not data_rows:
            continue

        if data_rows and _is_duplicate_header_row(data_rows[0], headers):
            data_rows = data_rows[1:]

        table_results = [
            {headers[i]: row[i] for i in range(len(headers))} for row in data_rows
        ]
        results.append(table_results)

    return results, list_type
