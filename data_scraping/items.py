import scrapy

class ArticleItem(scrapy.Item):
    source = scrapy.Field()
    mot_cle_recherche = scrapy.Field()
    titre = scrapy.Field()
    lien = scrapy.Field()
    auteurs = scrapy.Field()
    annee = scrapy.Field()
    abstract = scrapy.Field()
    journal = scrapy.Field()
    date_scraping = scrapy.Field()
    # Additional IEEE fields
    country = scrapy.Field()
    topic = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    date_pub = scrapy.Field()
