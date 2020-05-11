import logging
import collections
import csv

import requests
import bs4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url'
    ),
)

HEADERS = {
    'Бренд',
    'Товар',
    'Ссылка'
}


class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'Accept-language': 'ru'
        }
        self.result = []

    def load_page(self):
        url = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/vodolazki'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.dtList.i-dtList.j-card-item')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        # logger.info(block)
        # logger.info('m' * 100)

        url_block = block.select_one('a.ref_goods_n_p.j-open-full-product-card')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return

        name_block = block.select_one('div.dtlist-inner-brand-name')
        if not name_block:
            logger.error('no name_block on {url}')
            return

        brand_name = name_block.select_one('strong.brand-name')
        if not brand_name:
            logger.error('no brand_name on {url}')
            return

        # Wrangler /
        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = name_block.select_one('span.goods-name')
        if not goods_name:
            logger.error('no goods_name on {url}')
            return

        goods_name = goods_name.text.strip()

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))

        logger.debug('%s, %s, %s', url, brand_name, goods_name)
        logger.debug('-' * 100)

    def save_result(self):
        path = 'C:\Python\parserWildberries\wb\csvTest.csv'
        with open(path, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Получили {len(self.result)} элементов')

        self.save_result()


if __name__ == '__main__':
    parser = Client()
    parser.run()
