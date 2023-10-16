import json
import scrapy
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field


class QoteItem(Item):
    tags = Field()
    author = Field()
    quote = Field()


class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    location_born = Field()
    bio = Field()


class QuotesPipline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'fullname' in adapter.keys():
            self.authors.append({
                "fullname": adapter["fullname"],
                "born_date": adapter["born_date"],
                "location_born": adapter["location_born"],
                "bio": adapter["bio"],
                })
        if 'quote' in adapter.keys():
            self.quotes.append({
                "tags": adapter["tags"],
                "author": adapter["author"],
                "quote": adapter["quote"],
                })
        return

    def close_spider(self, spider):
        with open('quotes.json', 'w') as fd:
            json.dump(self.quotes, fd, indent=2)
        with open('authors.json', 'w') as fd:
            json.dump(self.authors, fd, indent=2)


class AuthorsSpider(scrapy.Spider):
    name = 'authors'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com']
    # custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "result.json"}
    custom_settings = {"ITEM_PIPELINES": {QuotesPipline: 300}}

    def parse(self, response, *_):
        for quote in response.xpath("/html//div[@class='quote']"):
            tags = quote.xpath("div[@class='tags']/a/text()").extract()
            author = quote.xpath("span/small/text()").get().strip()
            q = quote.xpath("span[@class='text']/text()").get()
            yield QoteItem(tags=tags, author=author, quote=q)
            yield response.follow(url=self.start_urls[0] + quote.xpath('span/a/@href').get(),
                                callback=self.nested_parse_author)

        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)

    def nested_parse_author(self, response, *_):
        author = response.xpath('/html//div[@class="author-details"]')
        fullname = author.xpath('h3[@class="author-title"]/text()').get()
        born_date = author.xpath('p/span[@class="author-born-date"]/text()').get()
        location_born = author.xpath('p/span[@class="author-born-location"]/text()').get()
        bio = author.xpath('div[@class="author-description"]/text()').get().strip()
        yield AuthorItem(fullname=fullname, born_date=born_date, location_born=location_born, bio=bio)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(AuthorsSpider)
    process.start()

