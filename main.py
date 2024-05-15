import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

BASE_URL = 'https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A94&page={}'

def parse_advisory_date(date_string: str) -> datetime:
    return datetime.strptime(date_string, '%b %d, %Y')

def scrape_advisories_from_page(url: str) -> list:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    advisories = soup.find_all('article', class_='is-promoted c-teaser c-teaser--horizontal')

    data = []

    for advisory in advisories:
        title = advisory.find('h3', class_='c-teaser__title').text.strip()
        date_string = advisory.find('div', class_='c-teaser__date').text.strip()
        advisory_date = parse_advisory_date(date_string)
        alert_code = advisory.find('div', class_='c-teaser__meta').text.strip()
        link = advisory.find('a')['href']
        full_link = f'https://www.cisa.gov{link}'

        advisory_data = {
            "Title": title,
            "Advisory Date": advisory_date.strftime('%Y-%m-%d'),
            "Alert Code": alert_code,
            "Link": full_link
        }
        data.append(advisory_data)

    return data

def scrape_all_advisories(start_date: datetime, end_date: datetime) -> list:
    all_data = []
    page_num = 0

    while True:
        url = BASE_URL.format(page_num)
        page_data = scrape_advisories_from_page(url)
        if not page_data:
            break
        all_data.extend(page_data)
        page_num += 1

    filtered_data = [item for item in all_data if start_date <= datetime.strptime(item["Advisory Date"], '%Y-%m-%d') <= end_date]

    return filtered_data

def main():
    while True:
        try:
            start_date_str = input("Enter start date (YYYY-MM-DD): ")
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid start date format, try again.")

    while True:
        try:
            end_date_str = input("Enter end date (YYYY-MM-DD): ")
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid end date format, try again.")

    all_data = scrape_all_advisories(start_date, end_date)

    with open('advisories.json', 'w') as f:
        json.dump(all_data, f, indent=4)

    print("Veri başarıyla advisories.json dosyasına kaydedildi.")

if __name__ == '__main__':
    main()