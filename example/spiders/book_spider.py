# -*- coding: UTF-8 -*-
import scrapy
from ..items import BooksItem


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/"]
    table = "books"
    # custom_settings = {
    #     'ITEM_PIPELINES': {'example.pipelines.SQLitePipeline': 300}}

    def parse(self, response):
        books = response.xpath('//*[@class="product_pod"]')
        print (len(books))
        for book in books:
            book_item = BooksItem()
            book_item["title"] = book.xpath("./h3/a/@title").extract_first()
            book_item["price"] = book.xpath("./div[2]/p[1]/text()").extract_first()
            yield book_item
        next_url = response.xpath(
            '//*[@class="next"]/a/@href').extract_first()
        if next_url:
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url, callback=self.parse)
