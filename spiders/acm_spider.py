import scrapy
from items import ArticleItem

class AcmSpider(scrapy.Spider):
    name = "acm"
    
    keywords = ['Blockchain', 'Deep Learning', 'Big Data']

    def start_requests(self):
        base_url = "https://dl.acm.org/action/doSearch?AllField={}"
        
        for keyword in self.keywords:
            url = base_url.format(keyword.replace(' ', '%20'))
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                meta={'keyword': keyword, 'selenium': True, 'wait_time': 5}
            )

    def parse(self, response):
        keyword = response.meta['keyword']
        
        articles = response.css('li.search__item, div.issue-item')
        
        self.logger.info(f"Found {len(articles)} articles for {keyword}")

        for article in articles[:10]:
            item = ArticleItem()
            item['source'] = 'ACM'
            item['mot_cle_recherche'] = keyword
            
            item['titre'] = article.css('h5.issue-item__title a::text, .hlFld-Title::text').get()
            
            rel_url = article.css('h5.issue-item__title a::attr(href)').get()
            if rel_url:
                item['lien'] = response.urljoin(rel_url)
            
            item['auteurs'] = article.css('ul.rlist--inline li a::text').getall()
            item['annee'] = article.css('span.dot-separator span::text').get()
            item['abstract'] = article.css('div.issue-item__abstract p::text').get()
            item['journal'] = article.css('.epub-section__title::text').get()
            
            if item['titre']:
                yield item
