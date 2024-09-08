import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class AiContentSpider(scrapy.Spider):
    name = "ai_content_spider"
    allowed_domains = ["medium.com", "substack.com"]
    
    # List of URLs to scrape for AI-related content
    start_urls = [
        "https://medium.com/tag/ai",
        "https://medium.com/tag/machine-learning",
        "https://substack.com/search/ai",
        "https://substack.com/search/machine-learning"
    ]
    
    custom_settings = {
        'USER_AGENT': 'OpenSEO Web Scraper (+http://yourdomain.com)',
        'DOWNLOAD_DELAY': 2,  # Delay to avoid overloading the server
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'AUTOTHROTTLE_ENABLED': True,  # Automatically throttle requests based on load
        'AUTOTHROTTLE_START_DELAY': 1,  # Initial download delay
        'AUTOTHROTTLE_MAX_DELAY': 5,  # Maximum download delay in case of high latencies
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,  # Average number of requests Scrapy should be sending in parallel to each remote server
        'ROBOTSTXT_OBEY': True,  # Respect robots.txt rules
    }

    def parse(self, response):
        # Scrape AI-related articles from Medium and Substack
        articles = response.xpath('//h3/text() | //h2/text() | //h1/text()').getall()

        for article in articles:
            yield {
                'title': article.strip(),
                'url': response.url,
                'source': response.url.split('/')[2]
            }

        # Follow pagination links, if any
        next_page = response.xpath('//a[contains(@class, "pagination")]/@href').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)

def run_spider():
    # Function to run the spider
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(AiContentSpider)
    process.start()

if __name__ == "__main__":
    run_spider()