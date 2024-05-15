import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

BASE_URL = 'https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A94&page={}'

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
        link = advisory.find('a')['href']

        advisory_data = {
            "Title": title,
            "Advisory Date": advisory_date.strftime('%Y-%m-%d'),
            "Alert Code": alert_code,
            "Link": link
        }
        data.append(advisory_data)

    return data

def scrape_all_advisories(start_date, end_date):
    all_data = []
    page_num = 0

    while True:
        url = BASE_URL.format(page_num)
        page_data = scrape_page(url)
        if not page_data:
            break
        all_data.extend(page_data)
        page_num += 1

    filtered_data = [item for item in all_data if start_date <= datetime.strptime(item["Advisory Date"], '%Y-%m-%d') <= end_date]

    return filtered_data

start_date = datetime(2022, 1, 1)
end_date = datetime.now()

all_data = scrape_all_advisories(start_date, end_date)

with open('advisories.json', 'w') as f:
    json.dump(all_data, f, indent=4)

print("Veri başarıyla advisories.json dosyasına kaydedildi.")
