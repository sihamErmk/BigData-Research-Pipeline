import scrapy
from items import ArticleItem

class ScienceDirectSpider(scrapy.Spider):
    name = "sciencedirect"
    
    keywords = ['Blockchain', 'Deep Learning', 'Big Data']

    def start_requests(self):
        base_url = "https://www.sciencedirect.com/search?qs={}"
        
        for keyword in self.keywords:
            url = base_url.format(keyword.replace(' ', '%20'))
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                meta={'keyword': keyword, 'selenium': True, 'wait_time': 5}
            )

    def parse(self, response):
        keyword = response.meta['keyword']
        
        articles = response.css('div.result-item, article.js-article')
        
        self.logger.info(f"Found {len(articles)} articles for {keyword}")

        for article in articles[:10]:
            item = ArticleItem()
            item['source'] = 'ScienceDirect'
            item['mot_cle_recherche'] = keyword
            
            item['titre'] = article.css('h2 a span::text, .result-list-title-link::text').get()
            
            rel_url = article.css('h2 a::attr(href)').get()
            if rel_url:
                item['lien'] = response.urljoin(rel_url)
            
            item['auteurs'] = article.css('.author span::text').getall()
            item['annee'] = article.css('.subtype-srctitle-date::text').get()
            item['abstract'] = article.css('.abstract-text::text').get()
            item['journal'] = article.css('.publication-title::text').get()
            
            if item['titre']:
                yield item
