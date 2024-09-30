import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_selenium import SeleniumRequest  # Import SeleniumRequest for dynamic content handling
from scrapy.linkextractors import LinkExtractor
from selenium.webdriver.common.by import By

class AiContentSpider(scrapy.Spider):
    name = "ai_content_spider"
    allowed_domains = ["medium.com", "substack.com"]

    # Start URLs to scrape for AI-related content
    start_urls = [
        "https://medium.com/tag/ai",
        "https://medium.com/tag/machine-learning",
        "https://substack.com/search/ai",
        "https://substack.com/search/machine-learning"
    ]

    custom_settings = {
        'USER_AGENT': 'OpenSEO Web Scraper',  # Update to your domain/contact info
        'DOWNLOAD_DELAY': 2,  # Delay to avoid overloading the server
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'AUTOTHROTTLE_ENABLED': True,  # Automatically throttle requests based on load
        'AUTOTHROTTLE_START_DELAY': 1,  # Initial download delay
        'AUTOTHROTTLE_MAX_DELAY': 5,  # Maximum download delay in case of high latencies
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,  # Average number of requests to be sent in parallel to each remote server
        'ROBOTSTXT_OBEY': True,  # Respect robots.txt rules
        'LOG_LEVEL': 'INFO',  # Set log level to INFO to track progress without clutter
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800,
        }
    }

    def start_requests(self):
        # Use SeleniumRequest to handle dynamic content
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=3,
                wait_until=lambda driver: driver.find_element(By.TAG_NAME, 'body')  # Correct way to wait for the body element
            )

    def parse(self, response):
        # Extract titles, headers, and other text elements
        articles = response.xpath('//h3/text() | //h2/text() | //h1/text()').getall()
        meta_description = response.xpath('//meta[@name="description"]/@content').get()
        headers = response.xpath('//h1//text() | //h2//text()').getall()

        for article in articles:
            yield {
                'title': article.strip(),
                'url': response.url,
                'source': response.url.split('/')[2]
            }

        # Yield additional data if meta description and headers are available
        if meta_description:
            yield {
                'meta_description': meta_description.strip(),
                'url': response.url,
                'source': response.url.split('/')[2]
            }

        if headers:
            for header in headers:
                yield {
                    'header': header.strip(),
                    'url': response.url,
                    'source': response.url.split('/')[2]
                }

        # Follow pagination links using a more flexible method
        link_extractor = LinkExtractor(allow_domains=self.allowed_domains, restrict_css='a.pagination, a[rel="next"]')
        for link in link_extractor.extract_links(response):
            yield SeleniumRequest(url=link.url, callback=self.parse, dont_filter=True)

    def handle_error(self, failure):
        self.logger.error(repr(failure))

def run_spider():
    # Function to run the spider
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(AiContentSpider)
    process.start()

if __name__ == "__main__":
    run_spider()