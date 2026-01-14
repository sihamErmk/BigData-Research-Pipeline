import scrapy
from items import ArticleItem

class IeeeSpider(scrapy.Spider):
    name = "ieee"
    
    keywords = ['Blockchain', 'Deep Learning', 'Big Data']

    def start_requests(self):
        base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText={}"
        
        for keyword in self.keywords:
            url = base_url.format(keyword.replace(' ', '%20'))
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                meta={'keyword': keyword, 'selenium': True, 'wait_time': 5}
            )

    def parse(self, response):
        keyword = response.meta['keyword']
        
        articles = response.css('div.List-results-items, xpl-results-item')
        
        self.logger.info(f"Found {len(articles)} articles for {keyword}")

        for article in articles[:10]:
            item = ArticleItem()
            item['source'] = 'IEEE'
            item['mot_cle_recherche'] = keyword
            
            item['titre'] = article.css('h2 a::text, h3 a::text').get()
            
            rel_url = article.css('h2 a::attr(href), h3 a::attr(href)').get()
            if rel_url:
                item['lien'] = response.urljoin(rel_url)
            
            item['auteurs'] = article.css('p.author span::text, .author-name::text').getall()
            item['annee'] = article.css('.publisher-info-container::text').get()
            item['abstract'] = article.css('.abstract-text::text').get()
            item['journal'] = article.css('.publisher-info::text').get()
            
            if item['titre']:
                yield item
