import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

def clean_text(text):
    return text.replace('\u00ae', '').replace('\u00a0', ' ').replace('\n', ' ').replace('\t', ' ').replace('\u2022', '-').replace('\u2019', "'").strip()

def parse_advisory_date(date_string: str) -> datetime:
    return datetime.strptime(date_string, '%b %d, %Y')

def process_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    content = []

    current_section = None
    for element in soup.find_all(['h3', 'h4', 'h5', 'p', 'table', 'tr', 'th', 'td', 'figure', 'div', 'li', 'ol']):
        if element.name in ['h3', 'h4', 'h5']:
            if current_section:
                content.append(current_section)
            current_section = {
                "type": "section",
                "data_title": element.text.strip(),
                "data": []
            }
        elif element.name == 'p':
            cleaned_text = clean_text(element.text.strip())
            if cleaned_text:
                if current_section is None:
                    current_section = {
                        "type": "section",
                        "data_title": "Untitled",
                        "data": []
                    }
                    content.append(current_section)
                if 'table' not in [parent.name for parent in element.parents]:
                    if not current_section["data"] or current_section["data"][-1]["type"] != "paragraph":
                        current_section["data"].append({"type": "paragraph", "data": cleaned_text})
                    else:
                        current_section["data"][-1]["data"] += ' ' + cleaned_text
        elif element.name == 'table':
            headers = [th.text.strip() for th in element.find_all('th')]
            rows = []
            for row in element.find_all('tr'):
                cols = [td.text.strip() for td in row.find_all('td')]
                if cols:
                    rows.append(cols)
            if current_section:
                current_section["data"].append({"type": "table", "header": headers, "data": rows})
        elif element.name in ['li', 'ol']:
            list_items = [li.text.strip() for li in element.find_all('li') if li.text.strip()]
            if list_items and current_section:
                current_section["data"].append({"type": "list", "items": list_items})
        elif element.name == 'figure':
            if current_section:
                img = element.find('img')
                if img and img.get('src'):
                    img_url = f"https://www.cisa.gov{img['src']}"
                    img_index = len(current_section["data"]) + 1
                    current_section["data"].append({"type": "image", "url": img_url, "index": img_index})
        elif element.name == 'div' and 'c-file__download' in element.get('class', []):
            if current_section:
                a_tag = element.find('a', href=True)
                if a_tag:
                    href = a_tag['href']
                    if href.endswith(('.pdf', '.json', '.xml')):
                        file_name = a_tag.text.strip()
                        file_link = f"https://www.cisa.gov{href}"
                        file_index = len(current_section["data"]) + 1
                        current_section["data"].append(
                            {"type": "file", "name": file_name, "url": file_link, "index": file_index})

    if current_section:
        content.append(current_section)

    return content

def scrape_advisories_from_page(url: str, start_date: datetime, end_date: datetime) -> list:
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
        if start_date <= advisory_date <= end_date:
            alert_code = advisory.find('div', class_='c-teaser__meta').text.strip()
            link = advisory.find('a')['href']
            full_link = f'https://www.cisa.gov{link}'

            advisory_data = {
                "title": title,
                "advisory_date": advisory_date.strftime('%Y-%m-%d'),
                "alert_code": alert_code,
                "link": full_link
            }

            try:
                response = requests.get(full_link)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error fetching advisory page: {e}")
                continue

            advisory_content = process_html_content(response.content)
            advisory_data['content'] = advisory_content

            data.append(advisory_data)

    return data

def scrape_all_advisories(start_date: datetime, end_date: datetime) -> list:
    all_data = []

    page_num = 0

    while True:
        url = f'https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A94&page={page_num}'
        page_data = scrape_advisories_from_page(url, start_date, end_date)

        if not page_data:
            break

        all_data.extend(page_data)

        page_num += 1

    return all_data

def save_advisories_to_json(advisories, date_folder):
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)

    for idx, advisory in enumerate(advisories):
        advisory_filename = f"{advisory['title']}-{idx}.json".replace('/', '_')
        output_folder = os.path.join(date_folder, advisory['advisory_date'])

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_path = os.path.join(output_folder, advisory_filename)

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(os.path.dirname(output_path)))

        with open(output_path, 'w') as f:
            json.dump(advisory, f, indent=4)

def main():
    while True:
        try:
            start_date_str = input("Enter Start Date (YYYY-MM-DD): ")
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid start date, please try again.")

    while True:
        try:
            end_date_str = input("Enter End Date (YYYY-MM-DD): ")
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid end date, please try again.")

    all_data = scrape_all_advisories(start_date, end_date)

    save_advisories_to_json(all_data, 'cisa_advisories')

    print("Data successfully saved to the 'cisa_advisories' folder.")

if __name__ == '__main__':
    main()