import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
import os
import subprocess
import time
import python_socks
import json
import re
import random

if not os.path.exists('parsed'):
    os.makedirs('parsed')

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.get_text()

def save_html(html_content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)

# Функция для поиска определенных шаблонов в тексте (например, email адресов)
def find_patterns(text, pattern):
    return re.findall(pattern, text)

# Функция для анализа форм на странице
def analyze_forms(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    forms = soup.find_all('form')
    return [str(form) for form in forms]

# Функция для получения всех изображений со страницы
def get_images(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    images = [img['src'] for img in soup.find_all('img', src=True)]
    return images

# Функция для анализа заголовков на странице
def analyze_headers(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    headers = {}
    for i in range(1, 7):
        headers[f'h{i}'] = [header.text for header in soup.find_all(f'h{i}')]
    return headers

# Функция для поиска всех внешних ссылок на странице
def find_external_links(html_content, base_url):
    soup = BeautifulSoup(html_content, 'lxml')
    links = set()
    for link in soup.find_all('a', href=True):
        if not link['href'].startswith(base_url):
            links.add(link['href'])
    return links

def find_scripts(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    return [script.get('src') or '' for script in soup.find_all('script')]

def extract_meta_tags(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    return {meta.get('name') or meta.get('property'): meta.get('content') for meta in soup.find_all('meta')}

def find_internal_links(html_content, base_url):
    soup = BeautifulSoup(html_content, 'lxml')
    return [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith(base_url)]

def find_html_comments(html_content):
    return [comment for comment in BeautifulSoup(html_content, 'html.parser').find_all(string=lambda text: isinstance(text, Comment))]

def extract_tables(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    return [str(table) for table in soup.find_all('table')]

# Функция для сравнения содержимого двух страниц
def compare_pages(content1, content2):
    return content1 == content2

# Функция для подсчета количества слов на странице
def count_words(text):
    return len(text.split())

def start_tor(tor_path):
    subprocess.Popen(tor_path)

async def async_is_link_active(session, url, retries=3):
    for attempt in range(retries):
        try:
            async with session.head(url, allow_redirects=True, timeout=30) as response:
                return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError, python_socks.ProxyError) as e:
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
            else:
                print(f"Error accessing {url}: {e}")
    return False


async def async_parse_onion_page(session, url):
    try:
        async with session.get(url, timeout=30) as response:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'lxml')
            title = soup.title.string if soup.title else 'No Title Found'
            links = [a['href'] for a in soup.find_all('a', href=True)]
            return title, html_content, links
    except aiohttp.ClientError as e:
        return f"Error: {e}", '', []

# Асинхронная функция для проверки активности ссылки
async def async_is_link_active(session, url, retries=3):
    for attempt in range(retries):
        try:
            async with session.head(url, allow_redirects=True, timeout=30) as response:
                return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError, python_socks.ProxyError):
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
    return False

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    ]
    return random.choice(user_agents)

async def async_main():
    tor_executable_path = 'tor/tor.exe'
    start_tor(tor_executable_path)
    time.sleep(10)  # Пауза для запуска Tor
    clear_console()

    onion_url = input("Добро пожаловать в парсер Tor сайтов!\nВведите .onion URL: ")

    headers = {'User-Agent': get_random_user_agent()}
    connector = ProxyConnector.from_url('socks5://127.0.0.1:9050')
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        title, html_content, links = await async_parse_onion_page(session, onion_url)
        print(f"Title: {title}")

        # Сохранение HTML-контента
        save_html(html_content, 'main_page.html')

        # Сохранение извлеченного текста
        text = extract_text(html_content)
        with open('parsed/extracted_text.txt', 'w', encoding='utf-8') as file:
            file.write(text)

        # Сохранение списка изображений
        images = get_images(html_content)
        with open('parsed/images_list.txt', 'w', encoding='utf-8') as file:
            for img in images:
                file.write(img + '\n')

        # Сохранение заголовков
        headers = analyze_headers(html_content)
        with open('parsed/headers.json', 'w', encoding='utf-8') as file:
            json.dump(headers, file, ensure_ascii=False, indent=4)

        # Сохранение внешних ссылок
        external_links = find_external_links(html_content, onion_url)
        with open('parsed/external_links.txt', 'w', encoding='utf-8') as file:
            for link in external_links:
                file.write(link + '\n')

        # Сохранение скриптов
        scripts = find_scripts(html_content)
        with open('parsed/scripts.txt', 'w', encoding='utf-8') as file:
            for script in scripts:
                file.write(script + '\n')

        # Сохранение метатегов
        meta_tags = extract_meta_tags(html_content)
        with open('parsed/meta_tags.json', 'w', encoding='utf-8') as file:
            json.dump(meta_tags, file, ensure_ascii=False, indent=4)

        forms = analyze_forms(html_content)
        with open('parsed/forms.txt', 'w', encoding='utf-8') as file:
            for form in forms:
                file.write(form + '\n\n')

        tasks = [async_is_link_active(session, link) for link in links]
        active_links = await asyncio.gather(*tasks)
        with open('parsed/active_links.txt', 'w', encoding='utf-8') as file:
            for link in links:
                active_link = await async_is_link_active(session, link)
                if active_link:
                    file.write(link + '\n')
                await asyncio.sleep(random.randint(1, 5))  # Задержка от 1 до 5 секунд

if __name__ == "__main__":
    asyncio.run(async_main())