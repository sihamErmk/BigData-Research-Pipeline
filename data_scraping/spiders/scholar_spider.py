import scrapy
from items import ArticleItem
from urllib.parse import quote

class ScholarSpider(scrapy.Spider):
    name = "scholar"
    
    keywords = [
        'Data Science', 'Machine Learning', 'Artificial Intelligence',
        'Deep Learning', 'Neural Networks', 'Big Data',
        'Data Mining', 'Natural Language Processing', 'Computer Vision',
        'Reinforcement Learning', 'Supervised Learning', 'Unsupervised Learning',
        'Classification', 'Regression', 'Clustering',
        'Random Forest', 'Decision Trees', 'Support Vector Machine',
        'Convolutional Neural Networks', 'Recurrent Neural Networks',
        'Transfer Learning', 'Feature Engineering', 'Model Optimization',
        'Predictive Analytics', 'Statistical Learning'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'ROBOTSTXT_OBEY': False,
    }

    def start_requests(self):
        base_url = "https://scholar.google.com/scholar?q={}"
        
        for keyword in self.keywords:
            url = base_url.format(quote(keyword))
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                meta={'keyword': keyword},
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

    def parse(self, response):
        keyword = response.meta['keyword']
        
        articles = response.css('div.gs_ri')
        
        self.logger.info(f"Found {len(articles)} articles for {keyword}")
        
        for article in articles[:20]:  # Increased to 20 articles per keyword
            item = ArticleItem()
            item['source'] = 'Google Scholar'
            item['mot_cle_recherche'] = keyword
            
            item['titre'] = article.css('h3.gs_rt a::text').get()
            item['lien'] = article.css('h3.gs_rt a::attr(href)').get()
            
            authors_year = article.css('div.gs_a::text').get()
            if authors_year:
                parts = authors_year.split('-')
                item['auteurs'] = [parts[0].strip()] if parts else []
                item['annee'] = parts[-1].strip()[:4] if len(parts) > 1 else None
            else:
                item['auteurs'] = []
                item['annee'] = None
            
            item['abstract'] = article.css('div.gs_rs::text').get()
            item['journal'] = article.css('div.gs_a::text').get()
            
            if item['titre']:
                yield item
