import csv
import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import nest_asyncio

nest_asyncio.apply()

load_dotenv()

# Get the path of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to urls.txt and previous_content.csv
urls_file_path = os.path.join(current_directory, 'urls.txt')
csv_file_path = os.path.join(current_directory, 'previous_content.csv')

# Line Notify token and headers
token = os.getenv('LINE_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/x-www-form-urlencoded'}

# User agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'

def handle_request_exception(e):
    """Handle exceptions from HTTP requests."""
    if isinstance(e, aiohttp.ClientResponseError):
        print(f'HTTP Error: {e}')
    elif isinstance(e, aiohttp.ClientConnectionError):
        print(f'Connection Error: {e}')
    elif isinstance(e, aiohttp.ClientTimeout):
        print(f'Timeout Error: {e}')
    elif isinstance(e, aiohttp.ClientError):
        print(f'Error: {e}')
    else:
        print(f'Unhandled Error: {e}')

# Function to send notifications via Line Notify
async def send_line_notification(session, message):
    payload = {'message': message}
    async with session.post('https://notify-api.line.me/api/notify', headers=headers, data=payload) as response:
        if response.status == 200:
            print('Message sent successfully!')
        else:
            print('Failed to send message.')
            print(await response.text())

# Function to read previous content from CSV
def read_previous_content():
    previous_content = {}
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    previous_content[row[0]] = row[1]
    except FileNotFoundError:
        return previous_content
    return previous_content

# Function to save the latest content to CSV
def save_previous_content(previous_content):
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        for url, content in previous_content.items():
            writer.writerow([url, content])

async def fetch_and_process_url(session, url, previous_content):
    if url.strip().startswith('skip-'):
        return

    try:
        async with session.get(url.strip(), headers={'User-Agent': USER_AGENT}) as response:
            response.raise_for_status()
            content = await response.read()

        soup = BeautifulSoup(content, 'html.parser')
        content_node = soup.select_one('#single > div.content > div.dt-breadcrumb.breadcrumb_bottom > ol > li:nth-child(3) > a > span')
        epall = soup.find_all('ul', class_='episodios')

        if content_node:
            content_text = content_node.text.strip()

            for ep in epall:
                selectep = ep.find_all('a', href=True)
                if selectep:
                    last_link = selectep[-1]
                    lastepisode = last_link.string + '\n' + 'ลิงก์:' + last_link['href']
                else:
                    content_text = 'ไม่เจอ'

            if url.strip() in previous_content and previous_content[url.strip()] != content_text:
                print(f'{previous_content[url.strip()]} \n มีตอนใหม่ \n ลิงก์::{lastepisode} \n ---------------------------------------------- ')
                await send_line_notification(session, lastepisode + '\n ---------------------------------------------- ')

            previous_content[url.strip()] = content_text

    except Exception as e:
        handle_request_exception(e)

async def main():
    async with aiohttp.ClientSession() as session:
        with open(urls_file_path, 'r') as file:
            urls = file.readlines()

        previous_content = read_previous_content()

        tasks = [fetch_and_process_url(session, url, previous_content) for url in urls]
        await asyncio.gather(*tasks)

        save_previous_content(previous_content)

if __name__ == '__main__':
    asyncio.run(main())
