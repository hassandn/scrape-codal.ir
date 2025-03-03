from playwright.sync_api import (
    sync_playwright,
)  # for fetching data from web page - and extract data from
from urllib.parse import urlencode  # for encoding parameters that you need for request
import requests  # for query


def generate_codal_url(
    Audited=None,
    AuditorRef=None,
    Category=None,
    Childs=None,
    CompanyState=None,
    CompanyType=None,
    Consolidatable=None,
    IndustryGroup=None,
    IsNotAudited=None,
    Length=None,
    LetterCode=None,
    LetterType=None,
    Mains=None,
    NotAudited=None,
    NotConsolidatable=None,
    PageNumber=None,
    Publisher=None,
    ReportingType=None,
    Symbol=None,
    TracingNo=None,
    search=True,
):  # parameters that you can use to search -> returns
    base_url = "https://search.codal.ir/api/search/v2/q"  # base url

    params = {
        "Audited": Audited,
        "AuditorRef": AuditorRef,
        "Category": Category,
        "Childs": Childs,
        "CompanyState": CompanyState,
        "CompanyType": CompanyType,
        "Consolidatable": Consolidatable,
        "IndustryGroup": IndustryGroup,
        "IsNotAudited": IsNotAudited,
        "Length": Length,
        "LetterCode": LetterCode,
        "LetterType": LetterType,
        "Mains": Mains,
        "NotAudited": NotAudited,
        "NotConsolidatable": NotConsolidatable,
        "PageNumber": PageNumber,
        "Publisher": Publisher,
        "ReportingType": ReportingType,
        "Symbol": Symbol,
        "TracingNo": TracingNo,
        "search": search,
    }  # set parameters

    # remove parameters that are None
    filtered_params = {k: v for k, v in params.items() if v is not None}

    return f"{base_url}?{urlencode(filtered_params)}"


def fetch_codal_data(url):  # search data -> returns list of urls that user searched it
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }  # use header to prevent ban from server

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # check http errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}


def extract_links(data):  # extract links from letters
    if not data:  # if its empty return nothing
        return []
    letters = data.get("Letters", [])
    links = []
    for letter in letters:  # get letter serial we need it for open pages
        letter_serial = letter["Url"].split("LetterSerial=")[-1].split("&")[0]
        full_link = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={letter_serial}&rt=0&let=6&ct=0&ft=-1&sheetId=20"
        links.append(full_link)

    return links


def find_valid_link(links):  # find page that table is there!

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for link in links:
        try:
            response = requests.get(
                url=link, headers=headers, allow_redirects=False, timeout=10
            )

            if response.status_code == 302:  # if it's get redirect skip
                print(f"Redirected: {link} -> {response.headers.get('Location')}")
                continue

            if (
                response.status_code == 200
            ):  # return response if you got 200 status code
                return link

        except requests.exceptions.RequestException as e:
            print(f"Request failed for {link}: {e}")

    return None  # if we didn't get 200 status code then it returns


def fetch_data_from_codal_letters(url, row_names=None, col_names=None):
    """
    Fetches data from a Codal letter webpage.
    - Extracts tables or headers from the given URL.
    - Searches for the specified row and column names.
    - Returns the corresponding cell value.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True
            )  # Launch browser in headless mode
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")  # Wait until network is idle

            result = None

            # Check if headers exist on the page
            headers_page = page.locator("header").all()
            headers_page_texts = [
                header.inner_text().strip() for header in headers_page
            ]

            if col_names and col_names[0] in headers_page_texts:
                # If the requested column is found in headers, find its index
                col_index = headers_page_texts.index(col_names[0])
                extracted_data = []

                for row_name, row_occurrence in row_names:
                    row_index = None
                    row_count = 0
                    for i, row in enumerate(extracted_data):
                        if row and row[0] == row_name:
                            row_count += 1
                            if row_count == row_occurrence:
                                row_index = i
                                break
                    if row_index is not None:
                        result = extracted_data[row_index][col_index]

            else:
                # If headers are not found, check for tables
                tables = page.locator("table").all()
                column_found = False

                for table in tables:
                    rows = table.locator("tr").all()
                    if len(rows) < 2:
                        continue  # Skip tables with less than 2 rows

                    # Extract header rows
                    row1_cells = rows[0].locator("th").all()
                    row2_cells = rows[1].locator("th").all()

                    headers_row1 = [cell.inner_text().strip() for cell in row1_cells]
                    headers_row2 = [cell.inner_text().strip() for cell in row2_cells]

                    col_index_map = {}
                    for i, col in enumerate(headers_row1):
                        if col:
                            col_index_map[col] = i
                    for i, col in enumerate(headers_row2):
                        if col:
                            col_index_map[col] = i

                    if col_names[0] in headers_row1 + headers_row2:
                        # Find column index based on occurrence
                        col_index = None
                        col_count = 1
                        occurrence = col_names[1]
                        for i, header in enumerate(headers_row1 + headers_row2):
                            if col_names[0] in header:
                                col_count += 1
                                if col_count == occurrence:
                                    i += 1
                                    col_index = i
                                    break

                        # Extract table body data
                        tbody = table.locator("tbody")
                        body_rows = tbody.locator("tr").all()
                        extracted_data = []

                        for row in body_rows:
                            cells = row.locator("td").all()
                            row_data = [cell.inner_text().strip() for cell in cells]
                            extracted_data.append(row_data)

                        # Find the requested row based on occurrence
                        for row_name, row_occurrence in row_names:
                            row_index = None
                            row_count = 0
                            for i, row in enumerate(extracted_data):
                                if row and row[0] == row_name:
                                    row_count += 1
                                    if row_count == row_occurrence:
                                        row_index = i
                                        break

                            if row_index is not None and col_index is not None:
                                result = extracted_data[row_index][col_index]
                                column_found = True
                                break

                if not column_found:
                    raise ValueError(
                        f"Column '{col_names[0]}' not found in any tables."
                    )

            return result if result else "No value found."

    except Exception as e:
        return f"Error occurred: {str(e)}"


def normalize_response_number(number_str):
    """
    Normalizes a financial number string.
    - Removes parentheses for negative numbers.
    - Removes commas.
    - Converts the string to an integer.
    """
    is_negative = False
    if number_str.startswith("(") and number_str.endswith(")"):
        is_negative = True
        number_str = number_str[1:-1]  # Remove parentheses

    number_str = number_str.replace(",", "")  # Remove commas
    number = int(number_str)  # Convert to integer

    return -number if is_negative else number  # Return with correct sign


def main():
    """
    Main function to fetch and process Codal data.
    - Generates Codal URL.
    - Extracts financial data from the letter.
    - Normalizes the extracted number.
    """
    url = generate_codal_url(
        Audited=True, CompanyType=1, IndustryGroup=27, Symbol="فولاد"
    )

    data = fetch_codal_data(url)
    letter_links = extract_links(data)
    valid_link = find_valid_link(letter_links)

    if valid_link:
        row_name = row_names = [("تختال", 1)]  # Row to search for
        col_name = ["مبلغ بهای تمام شده", 2]  # Column to search for
        extracted_data = fetch_data_from_codal_letters(valid_link, row_name, col_name)
        result = normalize_response_number(extracted_data)
        print(result)
    else:
        print("Response:", data if isinstance(data, dict) else data[:2])
