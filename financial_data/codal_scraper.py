from playwright.sync_api import (
    sync_playwright,
)  # for fetching data from web page - and extract data from
from urllib.parse import urlencode  # for encoding parameters that you need for request
import requests  # for query
from .models import ExtractedData, Log


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


def fetch_codal_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        Log.objects.create(
            log_detail=f"Request failed: {str(e)}",
            row=url,
            col=url,
        )
        return


def extract_links(data):
    if not data:
        return []
    letters = data.get("Letters", [])
    links = []
    for letter in letters:
        letter_serial = letter["Url"].split("LetterSerial=")[-1].split("&")[0]
        full_link = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={letter_serial}&rt=0&let=6&ct=0&ft=-1&sheetId=20"
        links.append(full_link)
    return links


def find_valid_link(links):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for link in links:
        try:
            response = requests.get(
                url=link, headers=headers, allow_redirects=False, timeout=10
            )
            if response.status_code == 302:
                print(f"Redirected: {link} -> {response.headers.get('Location')}")
                continue
            if response.status_code == 200:
                return link
        except requests.exceptions.RequestException as e:
            Log.objects.create(
                log_detail=f"Request failed for {link}: {str(e)}",
                row=link,
                col=link,
            )
    return None


def fetch_data_from_codal_letters(url, row_names, col_names):

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            result = None

            headers_page = page.locator("header").all()
            headers_page_texts = [
                header.inner_text().strip() for header in headers_page
            ]
            if col_names and col_names[0] in headers_page_texts:
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
                tables = page.locator("table").all()
                column_found = False
                for table in tables:
                    rows = table.locator("tr").all()
                    if len(rows) < 2:
                        continue
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

                        tbody = table.locator("tbody")
                        body_rows = tbody.locator("tr").all()
                        extracted_data = []
                        for row in body_rows:
                            cells = row.locator("td").all()
                            row_data = [cell.inner_text().strip() for cell in cells]
                            extracted_data.append(row_data)

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
                    Log.objects.create(
                        log_detail=f"Column '{col_names[0]}' not found in any tables.",
                        row=row_names,
                        col=col_names,
                    )
            return result if result else "No value found."
    except Exception as e:
        Log.objects.create(
            log_detail=f"Error occurred: {str(e)}",
            row=row_names,
            col=col_names,
        )
        return


def normalize_response_number(number_str):
    """
    Normalizes a financial number string.
    - Removes parentheses for negative numbers.
    - Removes commas.
    - Converts the string to an integer.
    """
    try:
        is_negative = False
        if number_str.startswith("(") and number_str.endswith(")"):
            is_negative = True
            number_str = number_str[1:-1]  # Remove parentheses

        number_str = number_str.replace(",", "")  # Remove commas

        # Check if the number_str is valid
        if not number_str.isdigit():
            raise ValueError(f"Invalid number: {number_str}")

        number = int(number_str)  # Convert to integer

        return -number if is_negative else number  # Return with correct sign
    except ValueError as e:
        Log.objects.create(
            log_detail=f"Error: {e}",
            row=number_str,
            col=number_str,
        )
        return 0  # Or handle the error in another way


def main(
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
    row_names=None,
    col_names=None,
):
    url = generate_codal_url(
        Audited=Audited,
        AuditorRef=AuditorRef,
        Category=Category,
        Childs=Childs,
        CompanyState=CompanyState,
        CompanyType=CompanyType,
        Consolidatable=Consolidatable,
        IndustryGroup=IndustryGroup,
        IsNotAudited=IsNotAudited,
        Length=Length,
        LetterCode=LetterCode,
        LetterType=LetterType,
        Mains=Mains,
        NotAudited=NotAudited,
        NotConsolidatable=NotConsolidatable,
        PageNumber=PageNumber,
        Publisher=Publisher,
        ReportingType=ReportingType,
        Symbol=Symbol,
        TracingNo=TracingNo,
    )

    data = fetch_codal_data(url)
    letter_links = extract_links(data)
    valid_link = find_valid_link(letter_links)

    if valid_link:
        extracted_data = fetch_data_from_codal_letters(valid_link, row_names, col_names)
        if extracted_data:
            normalized_data = normalize_response_number(extracted_data)
            # ذخیره‌سازی داده در مدل ExtractedData

            extracted_data_instance = ExtractedData.objects.create(
                data=normalized_data, row=row_names[0][0], col=col_names[0]
            )
            # print(normalized_data)
            # print(f"Data saved: {extracted_data_instance}")
        else:
            Log.objects.create(
                log_detail=f"No valid data found.",
                row=None,
                col=None,
            )
    else:
        # ذخیره خطا در مدل Log
        Log.objects.create(
            log_detail=f"Error: No valid link found for URL {url}",
            row=row_names,
            col=col_names,
        )
        Log.objects.create(
            log_detail=f"Error: No valid link found.",
            row=row_names,
            col=col_names,
        )
