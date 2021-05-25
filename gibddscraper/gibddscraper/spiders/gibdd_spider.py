import json

import scrapy
from scrapy_splash import SplashRequest
from w3lib.html import remove_tags
from scrapy.crawler import CrawlerProcess


class GibddSpider(scrapy.Spider):
    name = 'gibdd_spider'
    allowed_domains = ['xn--90adear.xn--p1ai']
    start_urls = ['https://xn--90adear.xn--p1ai/r/65/news/']

    lua_script = """function main(splash)
      splash:set_user_agent(splash.args.ua)
      assert(splash:go(splash.args.url))

      -- requires Splash 2.3  
      while not splash:select('ul.paginator') do
        splash:wait(0.1)
      end

      local entries = splash:history()
      local last_response = entries[#entries].response
      return {
        url = splash:url(),
        headers = last_response.headers,
        http_status = last_response.status,
        cookies = splash:get_cookies(),
        html = splash:html(),
      }
    end"""

    def start_requests(self):
        url = self.start_urls[0]
        print(f'url: {url}')
        yield SplashRequest(
            url=url, callback=self.parse_pages, endpoint='execute',
            args={
                'lua_source': self.lua_script,
                'ua': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
            },
        )

    def parse_pages(self, response, **kwargs):
        pages_list = response.css('ul.paginator').css('li').getall()
        last_page = int(remove_tags(pages_list[-1]))
        print(f'last page: {last_page}')
        last_page = 3
        for page in range(1, 1 + last_page, 1):
            url = f'https://xn--90adear.xn--p1ai/news/region?perPage=20&page={page}&region=65'
            yield scrapy.Request(url, headers={'x-requested-with': 'xmlhttprequest'}, callback=self.parse)

    def parse(self, response):
        json_response = json.loads(response.text)
        data = json_response['data']
        for item in data:
            yield item


def main():
    process = CrawlerProcess(settings={
        'FEED_URI': 'data/gibdd.json',
        'FEED_FORMAT': 'json',
        'SPLASH_URL': 'http://localhost:8050',
        'DOWNLOADER_MIDDLEWARES': {
            "scrapy_splash.SplashCookiesMiddleware": 723,
            "scrapy_splash.SplashMiddleware": 725,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
            },
        'SPIDER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
            },
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage',
    })

    process.crawl(GibddSpider)
    process.start()


if __name__ == '__main__':
    main()
