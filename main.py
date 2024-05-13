import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

base_url = 'https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A94&page={}'

def scrape_page(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    advisories = soup.find_all('article', class_='is-promoted c-teaser c-teaser--horizontal')

    data = []

    for advisory in advisories:
        title = advisory.find('h3', class_='c-teaser__title').text.strip()
        date_string = advisory.find('div', class_='c-teaser__date').text.strip()
        advisory_date = datetime.strptime(date_string, '%b %d, %Y')
        alert_code = advisory.find('div', class_='c-teaser__meta').text.strip()

        advisory_data = {
            "Title": title,
            "Advisory Date": advisory_date.strftime('%Y-%m-%d'),
            "Alert Code": alert_code,
        }
        data.append(advisory_data)

    return data

all_data = []

for page_num in range(15):
    url = base_url.format(page_num)
    print("Scraping:", url)
    page_data = scrape_page(url)
    all_data.extend(page_data)

json_data = json.dumps(all_data, indent=4)

print(json_data)
