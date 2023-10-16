import json
import scrapy
from scrapy.crawler import CrawlerProcess


class AuthorsSpider(scrapy.Spider):
    name = 'authors'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com']

    def __init__(self):
        self.quotes = []
        self.authors = []

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            author = quote.xpath("span/small/text()").get()
            if author not in self.authors:
                self.authors.append(author)

            quote_item = {
                "tags": quote.xpath("div[@class='tags']/a/text()").extract(),
                "author": author,
                "quote": quote.xpath("span[@class='text']/text()").get()
            }
            self.quotes.append(quote_item)

        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield response.follow(next_link, self.parse)

    def closed(self, reason):
        with open('quotes.json', 'w') as qf:
            json.dump(self.quotes, qf, indent=2)

        authors = []
        for author in self.authors:
            authors.append({
                "fullname": author,
                "born_date": "",
                "born_location": "",
                "description": ""
            })

        with open('authors.json', 'w') as af:
            json.dump(authors, af, indent=2)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(AuthorsSpider)
    process.start()
