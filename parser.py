import logging
import bs4
import requests
import collections
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')
ParseResult = collections.namedtuple('ParseResult', ('brand_name', 'goods_name', 'url', 'price'))
HEADERS = ("Бренд", "Товар", "Ссылка", 'Цена')


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36(KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
        }
        self.result = []

    def load_page(self, i):
        url = f'https://by.wildberries.ru/catalog/muzhchinam/odezhda/vodolazki?page={i}'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text)
        container = soup.select('div.dtList.i-dtList.j-card-item')
        for block in container:
            self.parse_block(block)

    def parse_block(self, block):
        url_block = block.select_one('a.ref_goods_n_p')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return

        price_block = block.select_one('span.price').text.split('к.')

        # #Wrangler price
        price = price_block[0]

        name_block = block.select_one('div.dtlist-inner-brand-name')
        if not url_block:
            logger.error(f'no name_block on {url}')
            return

        brand_name = name_block.select_one('strong.brand-name.c-text-sm')
        if not brand_name:
            logger.error(f'no brand_name on {url}')
            return

        # Wrangler /
        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = name_block.select_one('span.goods-name.c-text-sm').text.strip()
        if not goods_name:
            logger.error(f'no goods_name on {url}')
            return

        self.result.append(ParseResult(url=url, brand_name=brand_name, goods_name=goods_name, price=price))

        logger.debug('%s, %s, %s', url, brand_name, goods_name, price_block)
        logger.debug('-' * 100)

    def save_results(self):
        path = 'test.csv'
        with open(path, 'w')as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        for i in range(1, 23):
            text = self.load_page(i)
            self.parse_page(text=text)
            logger.info(f'Get {len(self.result)}')
        self.save_results()


if __name__ == '__main__':
    parser = Client()
    parser.run()
