import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from castellbank.items import Article


class CastellbankSpider(scrapy.Spider):
    name = 'castellbank'
    start_urls = ['https://www.castell-bank.de/ueber-uns/news/News_Aktuelles.html']

    def parse(self, response):
        links = response.xpath('(//div[@class="acc-inner"])[1]//li/aa[not(self::*[contains(@class,"btn")])]/@href/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        archive = 'https://www.castell-bank.de/ueber-uns/news/pressearchiv.html'
        yield response.follow(archive, self.parse_archive)

    def parse_archive(self, response):
        links = response.xpath('//main//ul//a[not(self::*[contains(@class,"btn")])]/@href')
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        date = ''
        if title:
            title = title.strip()
            if title[:2].isnumeric():
                date = title.split()[0]

        content = response.xpath('//div[@class="text"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
