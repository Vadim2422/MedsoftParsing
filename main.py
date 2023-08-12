import asyncio
import json
import random
import re

from bs4 import BeautifulSoup as bs

from aiohttp import ClientSession

base_url = 'https://medsi.ru'


async def get_page(url: str):
    async with ClientSession() as session:
        response = await session.get(url)
        return await response.text()


async def save_photo(url: str, filename: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            photo = await response.read()
    with open(f"src/{filename}", 'wb') as f:
        f.write(photo)


async def main():
    # html = bs(await get_page("https://medsi.ru/doctors/plokhov-vladimir-nikolaevich/"), 'html.parser')
    # with open("doc.html", 'w') as f:
    #     f.write(await get_page("https://medsi.ru/doctors/plokhov-vladimir-nikolaevich/"))

    with open("links.json", 'r') as f:
        links = json.load(f)

    for i, link in enumerate(links):
        html = bs(await get_page(link), 'html.parser')

        # FIO
        fio = html.find('div', class_='med-page-banner__content med-page-banner__content_finaly-target').find('h1',
                                                                                                              class_='med-page-banner__title').text.strip()

        # Work experience
        work_experience = re.search(r'\d+',
                                    html.find('span', class_='__bold', string='Стаж работы:').parent.text).group()
        # print(work_experience)

        # Category
        category = list(html.find('span', class_='__bold',
                                  string='Ученая степень / Категория / Ученое звание:').parent.stripped_strings)[
            1].replace('.', '')

        # Specialization
        specialization = [spec.text.replace(' ', ' ') for spec in
                          html.find('span', class_='__bold', string='Специализация:').parent.find('ul').find_all('li')]

        # Info
        info = html.find('div', class_='doctor-detail__position').find('p').text.replace(' ', ' ')

        # Price
        # price = int(html.find('div', class_='sign-up-doctor__price-cost').text.strip()[:-1].replace(' ', ''))

        # Photo
        photo = base_url + \
                html.find('div', class_='doctor-detail__img-block').find('div').find('img',
                                                                                     attrs={"itemprop": "image"})[
                    'src']
        await save_photo(photo, photo[photo.rfind('/')+1:])

        d = {
            "fio": fio,
            "work_experience": work_experience,
            "category": category,
            "specialization": specialization,
            "info": info,
            "price": random.randrange(500, 5000, 100),
            "photo": photo[photo.rfind('/')+1:]
        }

        with open(f"data/{i}.json", 'w',  encoding="utf-8") as f:
            json.dump(d, f, indent=4, ensure_ascii=False)


asyncio.run(main())
