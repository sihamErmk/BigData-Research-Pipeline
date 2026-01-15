import pymongo
from datetime import datetime
import hashlib

class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.duplicates_skipped = 0
        self.items_inserted = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017/'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'research_db')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # Drop existing index if it exists and recreate
        try:
            self.db['articles'].drop_index('lien_1')
        except:
            pass
        # Remove duplicates before creating unique index
        pipeline = [
            {"$group": {"_id": "$lien", "uniqueIds": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(self.db['articles'].aggregate(pipeline))
        for doc in duplicates:
            # Keep first, delete rest
            ids_to_delete = doc['uniqueIds'][1:]
            self.db['articles'].delete_many({"_id": {"$in": ids_to_delete}})
        # Create unique index
        self.db['articles'].create_index('lien', unique=True)

    def close_spider(self, spider):
        print(f"\n=== STATISTICS ===")
        print(f"Items inserted: {self.items_inserted}")
        print(f"Duplicates skipped: {self.duplicates_skipped}")
        print(f"Total in DB: {self.db['articles'].count_documents({})}")
        self.client.close()

    def process_item(self, item, spider):
        item['date_scraping'] = datetime.now()
        
        try:
            # Try to insert, will fail if duplicate link exists
            self.db['articles'].insert_one(dict(item))
            self.items_inserted += 1
        except pymongo.errors.DuplicateKeyError:
            # Skip duplicate
            self.duplicates_skipped += 1
            spider.logger.debug(f"Duplicate skipped: {item.get('titre', 'Unknown')}")
        
        return item
