from bs4 import BeautifulSoup
import datetime
import json
import asyncio
import aiohttp

from config import load_config

config = load_config('.env')
cookie = config.cookie.cookie

SUBJECTS_NAME = {}
HUBS_NAME = {}

url = 'https://habr.com'
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Cookie': cookie,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'x-app-version': '2.172.0',
}


def subjects_for_menu():
    with open('../publisher-bot/scraps/all_subjects.json', 'r', encoding='utf-8') as file:
        source = json.load(file)

    return source.get('subjects')


def hubs_for_menu(subject_list: list):
    subject_for_hub = []

    with open('../publisher-bot/scraps/all_hubs.json', 'r', encoding='utf-8') as file:
        source = json.load(file)

    for hub in subject_list:
        subject_for_hub.extend(source.get(hub))

    return subject_for_hub


def subsite_for_menu():
    with open('../publisher-bot/scraps/all_subsite.json', encoding='utf-8') as file:
        source = json.load(file)

    return source.get('subsites')


async def get_news(user_storage, user_id: int):
    print(f'USER STORAGE: {user_storage}')
    new_news_list = []

    hubs_keys_name = user_storage[user_id].keys()

    for key in hubs_keys_name:
        async with aiohttp.ClientSession(headers=headers) as session:
            await asyncio.sleep(5)
            async with session.get(f'https://habr.com/ru/hubs/{key}/articles/') as response:
                response_from_site = await response.text(encoding='utf-8')
                source = BeautifulSoup(response_from_site, 'lxml')

                article_block = source.find('div', class_='tm-articles-list').find_all('div', class_='tm-article-snippet tm-article-snippet')
                for value in article_block:
                    article_data = value.find('div', class_='tm-article-snippet__meta-container').find('div',class_='tm-article-snippet__meta').find('a', class_='tm-article-datetime-published tm-article-datetime-published_link').find('time').get('datetime').replace('Z', '')
                    article_other_hub = value.find('div', class_='tm-publication-hubs__container').find('div', class_='tm-publication-hubs').find_all('span', class_='tm-publication-hub__link-container')
                    article_description = value.find('div', class_='tm-article-body tm-article-snippet__lead').find('div', class_='article-formatted-body article-formatted-body article-formatted-body_version-2')

                    if datetime.datetime.strptime(article_data, "%Y-%m-%dT%H:%M:%S.%f") >= (user_storage[user_id][key]['last_check_in'] - datetime.timedelta(hours=8)):
                        article_url = url + value.find('h2', class_='tm-title tm-title_h2').find('a', class_='tm-title__link').get('href')
                        article_title = value.find('h2', class_='tm-title tm-title_h2').find('a', class_='tm-title__link').find('span').text
                        article_other_hub = [other_hubs.find('a').find('span').text for other_hubs in article_other_hub]
                        try:
                            article_description = [article_description.text]
                        except AttributeError as attr:
                            print(f'произошел {attr}')
                            article_description = ['нет описания']

                        new_news_list.append([article_url, article_title, article_other_hub, key, article_description])
    return new_news_list


async def get_subject_for_json():
    # await asyncio.sleep(100_000)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f'{url}/ru/hubs/') as action:

            with open('/publisher-bot/scraps/hubs.html', 'w', encoding='utf-8') as file:
                file.write(await action.text())

            soup = BeautifulSoup(await action.text(), 'lxml')
            subject_name = soup.find_all('a', class_='tm-main-menu__item')

            subject_keys_values = zip(
                [hub.text.strip() for hub in subject_name if hub.text.strip() not in ['Все потоки', 'Моя лента']],
                [hub.get('href').rstrip('/').split('/')[-1] for hub in subject_name if hub.get('href').rstrip('/').split('/')[-1] not in ['feed', 'articles', 'all']])
            SUBJECTS_NAME['subjects'] = list(subject_keys_values)

            with open('/publisher-bot/scraps/all_subjects.json', 'w', encoding='utf-8') as file:
                json.dump(SUBJECTS_NAME, file, indent=4, ensure_ascii=False)


async def get_hubs_for_json():
    await asyncio.sleep(100_000)
    last_page = 0
    with open('/publisher-bot/scraps/all_subjects.json', 'r', encoding='utf-8') as file:
        value_json = json.load(file)

    hubs = [hubs_data[1] for hubs_data in value_json.get('subjects')]

    for hub in hubs:
        with open('/publisher-bot/scraps/hubs.html', encoding='utf-8') as file_for_page:
            source = file_for_page.read()

        soup = BeautifulSoup(source, 'lxml')
        page_count = soup.find_all(class_='tm-pagination__pages')

        for page in page_count:
            last_page = (max([int(value) for value in page.text.replace('...', '').split()]))

        hub_name_list = []
        hub_url_list = []

        for page in range(1, last_page + 1):
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f'https://habr.com/ru/flows/{hub}/hubs/page{page}/') as response:
                    text = await response.text(encoding='utf-8')

                    # with open(f'D://new-folder/publisher_bot/scraps/{hub}{page}.html', 'w', encoding='utf-8') as hubs_file:
                    #     hubs_file.write(text)

                    soup = BeautifulSoup(text, 'lxml')
                    hubs_info = soup.find_all('div', class_='tm-hub__info')

                    for value in hubs_info:
                        title = value.find('a').text
                        title_url = value.find('a').get('href').rstrip('/').split('/')[-1]
                        hub_name_list.append(title)
                        hub_url_list.append(title_url)
                list_zip = zip(hub_name_list, hub_url_list)
                HUBS_NAME[hub] = list(list_zip)

    with open('/publisher-bot/scraps/all_hubs.json', 'w', encoding='utf-8') as file:
        json.dump(HUBS_NAME, file, indent=4, ensure_ascii=False)
