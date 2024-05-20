import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

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
        url = f'https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A94&page={page_num}'
        page_data = scrape_advisories_from_page(url)
        if not page_data:
            break
        all_data.extend(page_data)
        page_num += 1

    filtered_data = [item for item in all_data if start_date <= datetime.strptime(item["Advisory Date"], '%Y-%m-%d') <= end_date]

    return filtered_data

def save_advisories_to_json(advisories, date_folder):
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)

    for idx, advisory in enumerate(advisories):
        advisory_filename = f"{advisory['Title']}-{idx}.json"
        output_folder = os.path.join(date_folder, advisory['Advisory Date'])

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        date_subfolder = os.path.join(output_folder, os.path.basename(advisory['Link']))

        if not os.path.exists(date_subfolder):
            os.makedirs(date_subfolder)

        sub_folder = os.path.join(date_subfolder, os.path.basename(advisory['Link'].split('/')[0]))

        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)

        output_path = os.path.join(sub_folder, advisory_filename)

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        with open(output_path, 'w') as f:
            json.dump(advisory, f, indent=4)

def main():
    while True:
        try:
            start_date_str = input("Başlangıç Tarihini Girin (YYYY-AA-GG): ")
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Geçersiz başlangıç tarihi,tekrar deneyin.")

    while True:
        try:
            end_date_str = input("Bitiş Tarihini Seçin (YYYY-AA-GG): ")
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Geçersiz bitiş tarihi,tekrar deneyin.")

    all_data = scrape_all_advisories(start_date, end_date)

    save_advisories_to_json(all_data, 'cisa_advisories')

    print("Veri başarıyla cisa\_advisories klasörüne kaydedildi.")

if __name__ == '__main__':
    main()