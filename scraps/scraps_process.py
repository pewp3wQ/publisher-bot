from bs4 import BeautifulSoup
import datetime

import json
import asyncio
import aiohttp

SUBJECTS_NAME = {}
HUBS_NAME = {}

url = 'https://habr.com'
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': '_ym_uid=1640843634111208880; habr_uuid=QXpQNUNxRlk2UmN6azhtUGlSK2lMZHlQNG9tYUh0bWRZZzVCMm1zbVZpWitVbHZVdEpSeXQxdVJldGNlcXplRw%3D%3D; hl=ru; fl=ru; mp_e2d341d0f1fa432ebeafb8f954b334b2_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A18cf169ed2fb57-021a515f2475bb-26001951-1fa400-18cf169ed2fb57%22%2C%22%24device_id%22%3A%20%2218cf169ed2fb57-021a515f2475bb-26001951-1fa400-18cf169ed2fb57%22%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.com%22%7D; _ga_8ZVM81B7DF=GS1.1.1704857299.1.1.1704857317.0.0.0; __gads=ID=5b2c56d176f65c77:T=1706150354:RT=1706150793:S=ALNI_Mb8SWhLxoS_UHdgSPyCRQtK_p1idg; FCCDCF=%5Bnull%2Cnull%2Cnull%2C%5B%22CP6lk0AP6lk0AEsACBENApEgAAAAAEPgACiQAAAOhQD2F2K2kKFkPCmQWYAQBCijYEAhQAAAAkCBIAAgAUgQAgFIIAgAIFAAAAAAAAAQEgCQAAQABAAAIACgAAAAAAIAAAAAAAQQAAAAAIAAAAAAAAEAAAAAAAQAAAAIAABEhCAAQQAEAAAAAAAQAAAAAAAAAAABAAA.YAAAAAAAAAA%22%2C%222~~dv.2072.70.89.93.108.122.149.196.2253.2299.259.2357.311.313.323.2373.338.358.2415.415.449.2506.2526.486.494.495.2568.2571.2575.540.574.2624.609.2677.864.981.1029.1048.1051.1095.1097.1126.1201.1205.1211.1276.1301.1344.1365.1415.1423.1449.1451.1570.1577.1598.1651.1716.1735.1753.1765.1870.1878.1889.1958%22%2C%223A5D05AE-A498-4D0D-A315-711A3CEF0232%22%5D%5D; __eoi=ID=4896a1bf619f07fb:T=1708910663:RT=1708910663:S=AA-AfjYZiqJyWPRlk_NhqKDyLXYQ; _ym_d=1710161246; _ga_VMM2ZGEV9D=GS1.1.1710163065.1.1.1710163090.0.0.0; _ga_G589K88PTZ=GS1.1.1710197322.2.0.1710197322.0.0.0; habrsession_id=habrsession_id_078d4605f717214f947868d5102a568c; PHPSESSID=6ronh3us4jvkkr0fn095kev2tj; hsec_id=8ddf2d60cc48adf4200743e5c7d079b1; habr_web_ga_uid=ed5dab97bfae845a37679fd96ec2d5a8; habr_web_hide_ads=false; habr_web_user_id=3676583; connect_sid=s%3A5FjG3TIN4hYVHPN3tTaTA28R6d0SAUmd.lHqh9Ko4wAy2plI3Tk0%2FL3WiDhsTx4W5kaA9mY9R8QI; _ga_2KY4NGC881=GS1.2.1710287271.1.1.1710287506.21.0.0; _ga=GA1.1.707459592.1701142988; habr_web_flow_filter_news_all=/news/; habr_article_view=cards; _ga_DDTJ1S3PQZ=GS1.1.1710979496.3.0.1710979496.0.0.0; habr_web_home_feed=/articles/; _ga_EDKVH06JKZ=GS1.1.1711013401.4.1.1711013487.0.0.0; target-minor-version=172; _ym_isad=1; visited_articles=803421:783398:763866:786754:141411:801765:801825:732136:796365:800065; _ga_S28W1WC23F=GS1.1.1711667843.119.0.1711667843.60.0.681199865',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Referer': 'https://habr.com/ru/hubs/infosecurity/articles/',
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
    with open('D://new-folder/publisher_bot/scraps/all_subjects.json', 'r', encoding='utf-8') as file:
        source = json.load(file)

    return source.get('subjects')


def hubs_for_menu(subject_list: list):
    subject_for_hub = []

    with open('D://new-folder/publisher_bot/scraps/all_hubs.json', 'r', encoding='utf-8') as file:
        source = json.load(file)

    for hub in subject_list:
        subject_for_hub.extend(source.get(hub))

    return subject_for_hub


def subsite_for_menu():
    with open('D://new-folder/publisher_bot/scraps/all_subsite.json', encoding='utf-8') as file:
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

            with open('D://new-folder/publisher_bot/scraps/hubs.html', 'w', encoding='utf-8') as file:
                file.write(await action.text())

            soup = BeautifulSoup(await action.text(), 'lxml')
            subject_name = soup.find_all('a', class_='tm-main-menu__item')

            subject_keys_values = zip(
                [hub.text.strip() for hub in subject_name if hub.text.strip() not in ['Все потоки', 'Моя лента']],
                [hub.get('href').rstrip('/').split('/')[-1] for hub in subject_name if hub.get('href').rstrip('/').split('/')[-1] not in ['feed', 'articles', 'all']])
            SUBJECTS_NAME['subjects'] = list(subject_keys_values)

            with open('D://new-folder/publisher_bot/scraps/all_subjects.json', 'w', encoding='utf-8') as file:
                json.dump(SUBJECTS_NAME, file, indent=4, ensure_ascii=False)


async def get_hubs_for_json():
    # await asyncio.sleep(100_000)
    last_page = 0
    with open('D://new-folder/publisher_bot/scraps/all_subjects.json', 'r', encoding='utf-8') as file:
        value_json = json.load(file)

    hubs = [hubs_data[1] for hubs_data in value_json.get('subjects')]

    for hub in hubs:
        with open('D://new-folder/publisher_bot/scraps/hubs.html', encoding='utf-8') as file_for_page:
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

    with open('D://new-folder/publisher_bot/scraps/all_hubs.json', 'w', encoding='utf-8') as file:
        json.dump(HUBS_NAME, file, indent=4, ensure_ascii=False)
