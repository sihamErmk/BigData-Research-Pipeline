import scrapy
from items import ArticleItem

class TestSpider(scrapy.Spider):
    name = "test"
    
    def start_requests(self):
        # Test with a simple, reliable site
        yield scrapy.Request(
            'https://example.com', 
            callback=self.parse,
            meta={'selenium': True, 'wait_time': 2}
        )

    def parse(self, response):
        self.logger.info(f"Page title: {response.css('h1::text').get()}")
        
        # Create a test item
        item = ArticleItem()
        item['source'] = 'Test'
        item['mot_cle_recherche'] = 'test'
        item['titre'] = 'Test Article - ' + response.css('h1::text').get()
        item['lien'] = response.url
        item['auteurs'] = ['Test Author']
        item['annee'] = '2024'
        item['abstract'] = 'This is a test article to verify the scraper works'
        item['journal'] = 'Test Journal'
        
        yield item
        self.logger.info("Test item created successfully!")
