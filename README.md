# CISA Cybersecurity Advisories Scraper

This Python script fetches cybersecurity advisories data from the CISA (Cybersecurity and Infrastructure Security Agency) website and saves it in JSON format.

## How It Works

1. It utilizes the `requests`, `BeautifulSoup`, `datetime`, and `json` libraries.
2. HTTP requests (`requests`) are sent to fetch data from the CISA website.
3. The page content is analyzed using `BeautifulSoup`, and relevant information (such as title, date, etc.) is extracted.
4. Date information is processed using the `datetime` module.
5. The extracted data is saved in JSON format using the `json` library.

