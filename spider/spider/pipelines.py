# -*- coding: utf-8 -*-

import pymongo


class CustomerReportsPipeline(object):

    """Responsible to store the scraped data into a MongoDB database.

    All the scraped and parsed items are submitted through this
    pipeline. To avoid catching duplicate items, only items posted in
    previous dates (not the current date) are considered.
    A MongoDB remote server is used to store the JSON-like objects. All
    settings for remote DB connection are stored in settings.py.

    Attributes
    ----------
    collection_name: str
        defines the MongoDB collection name to store the items

    Methods
    -------
    from_crawler(cls, clawler)
        Creates a new pipeline instance from the Crawler
    open_spider(self, spider)
        Creates a new MongoDB client
    close_spider(self, spider)
        Close the MongoDB client connection
    process_item(self, item, spider)
        Stores the scraped item into the database
    """

    collection_name = 'bigpy_customerreports'

    def __init__(self, mongo_uri, mongo_db):
        """
        Parameters
        ----------
        mongo_uri : string
            MongoDB remote database server address
        mongo_db : string
            MongoDB database name
        """

        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        """Creates a new pipeline instance from the Crawler

        Provides access to Scrapy components, like settings and signals
        that allows the pipeline to hook its functionalities.

        Returns
        -------
        instance
            the pipeline instance instance
        """

        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB')
        )

    def open_spider(self, spider):
        """Creates a new MongoDB client

        This method is invoked whenever the spider is called.
        """

        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        """Close the MongoDB client connection."""

        self.client.close()

    def process_item(self, item, spider):
        """Stores the scraped item into the database.

        Returns
        -------
        object
            The scraped item to continue the pipelines chain
        """

        crawled_items = dict(item)
        parsed_items = dict()

        for key in crawled_items:
            parsed_items[key] = crawled_items[key][0]

        self.db[self.collection_name].insert_one(parsed_items)

        return item
