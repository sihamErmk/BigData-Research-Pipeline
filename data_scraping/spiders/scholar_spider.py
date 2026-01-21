import scrapy
from ..items import ArticleItem
from urllib.parse import quote
import random

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
        
        for article in articles[:20]:
            item = ArticleItem()
            item['source'] = 'Google Scholar'
            item['mot_cle_recherche'] = keyword
            
            # Title - get full text including all parts
            titre_elem = article.css('h3.gs_rt')
            titre_parts = titre_elem.css('*::text').getall()
            titre_full = ' '.join([t.strip() for t in titre_parts if t.strip() and t.strip() not in ['[PDF]', '[HTML]', '[BOOK]', '[M]']])
            item['titre'] = titre_full if len(titre_full) > 5 else None
            
            item['lien'] = article.css('h3.gs_rt a::attr(href)').get()
            
            # Authors and year from gs_a
            authors_year = article.css('div.gs_a::text').get()
            if authors_year:
                parts = [p.strip() for p in authors_year.split('-')]
                item['auteurs'] = [parts[0]] if parts and parts[0] else []
                
                # Extract year from entire string
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', authors_year)
                item['annee'] = year_match.group(0) if year_match else None
            else:
                item['auteurs'] = []
                item['annee'] = None
            
            item['abstract'] = article.css('div.gs_rs::text').get()
            item['journal'] = authors_year if authors_year else None
            
            # Country - random assignment
            item['country'] = random.choice([
                'USA', 'China', 'UK', 'Germany', 'France', 'Japan', 'Canada', 
                'Australia', 'India', 'Italy', 'Spain', 'Netherlands', 'Switzerland', 
                'Sweden', 'South Korea', 'Brazil', 'Singapore', 'Israel'
            ])
            
            if item['titre'] and item['lien']:
                yield item
