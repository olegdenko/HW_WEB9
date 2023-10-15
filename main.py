import json
import scrapy
from scrapy.crawler import CrawlerProcess


class AuthorsSpider(scrapy.Spider):
    name = 'authors'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        quotes = []
        authors = []
        for quote in response.xpath("/html//div[@class='quote']"):
            quote_item = {
                        "keywords": quote.xpath("div[@class='tags']/a/text()").extract(),
                        "author": quote.xpath("span/small/text()").extract(),
                        "quote": quote.xpath("span[@class='text']/text()").get()
                        }
            quotes.append(quote_item)
            author = quote_item["author"]
            if author not in authors:
                authors.append(author)

        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)

        with open('quotes.json', 'w') as quotes_file:
            json.dump(quotes, quotes_file, indent=2)

        with open('authors.json', 'w') as authors_file:
            json.dump(authors, authors_file, indent=2)



if __name__ == "__main__":
    
    process = CrawlerProcess()
    process.crawl(AuthorsSpider)
    process.start()
