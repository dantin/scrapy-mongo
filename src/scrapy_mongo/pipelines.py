# -*- coding: utf-8 -*-
import datetime
import logging

from pymongo import errors
from pymongo.mongo_client import MongoClient
from pymongo.read_preferences import ReadPreference
from scrapy.exporters import BaseItemExporter

logger = logging.getLogger(__name__)


# Item Exporters are used to export/serialize items into different formats.
class MongoDBPipeline(BaseItemExporter):
    """ MongoDB pipeline class """
    # Default options
    config = {
        'uri': 'mongodb://localhost:27017',
        'fsync': False,  # whether to wait for replica
        'write_concern': 0,
        'database': 'scrapy-mongodb',
        'collection': 'items',
        'unique_key': None,
        'buffer': None,
        'append_timestamp': False,
        'stop_on_duplicate': 0,
    }

    # Item buffer
    current_item = 0
    item_buffer = []

    # Duplicate key occurrence count
    duplicate_key_count = 0

    def __init__(self, **kwargs):
        super(MongoDBPipeline, self).__init__(**kwargs)
        self.crawler = None
        self.settings = None
        self.collection = None
        self.stop_on_duplicate = 0

    def load_spider(self, spider):
        self.crawler = spider.crawler
        self.settings = spider.settings

    def configure(self):
        """ Configure the MongoDB connection """
        # Set all regular options
        options = [
            ('uri', 'MONGODB_URI'),
            ('fsync', 'MONGODB_FSYNC'),
            ('write_concern', 'MONGODB_REPLICA_SET_W'),
            ('database', 'MONGODB_DATABASE'),
            ('collection', 'MONGODB_COLLECTION'),
            ('unique_key', 'MONGODB_UNIQUE_KEY'),
            ('buffer', 'MONGODB_BUFFER_DATA'),
            ('append_timestamp', 'MONGODB_ADD_TIMESTAMP'),
            ('stop_on_duplicate', 'MONGODB_STOP_ON_DUPLICATE')
        ]

        for key, setting in options:
            if self.settings[setting]:
                self.config[key] = self.settings[setting]

        # Check for illegal configuration
        if self.config['buffer'] and self.config['unique_key']:
            logger.error((
                u'Illegal Config: Settings both MONGODB_BUFFER_DATA '
                u'and MONGODB_UNIQUE_KEY is not supported'
            ))
            raise SyntaxError((
                u'Illegal Config: Settings both MONGODB_BUFFER_DATA '
                u'and MONGODB_UNIQUE_KEY is not supported'
            ))

    def open_spider(self, spider):
        """ Method called when the spider is closed
        :param spider: BaseSpider object
        :return: None
        """
        self.load_spider(spider)

        # Configure the connection
        self.configure()

        connection = MongoClient(
                self.config['uri'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY)

        # Set up the collection
        database = connection[self.config['database']]
        self.collection = database[self.config['collection']]
        logger.info(u'Connected to MongoDB {0}, using "{1}/{2}"'.format(
                self.config['uri'],
                self.config['database'],
                self.config['collection']))

        # Ensure unique index
        if self.config['unique_key']:
            self.collection.ensure_index(self.config['unique_key'], unique=True)
            logger.info(u'Ensuring index for key {0}'.format(
                    self.config['unique_key']))

        # Get the duplicate on key option
        if self.config['stop_on_duplicate']:
            tmpValue = self.config['stop_on_duplicate']
            if tmpValue < 0:
                logger.error(
                        (
                            u'Negative values are not allowed for'
                            u' MONGODB_STOP_ON_DUPLICATE option.'
                        )
                )
                raise SyntaxError(
                        (
                            'Negative values are not allowed for'
                            ' MONGODB_STOP_ON_DUPLICATE option.'
                        )
                )
            self.stop_on_duplicate = self.config['stop_on_duplicate']
        else:
            self.stop_on_duplicate = 0

    def process_item(self, item, spider):
        """ Process the item and add it to MongoDB
        :type item: Item object
        :param item: The item to put into MongoDB
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: Item object
        """
        item = dict(self._get_serialized_fields(item))

        if self.config['buffer']:
            self.current_item += 1

            if self.config['append_timestamp']:
                item['scrapy-mongodb'] = {'ts': datetime.datetime.utcnow()}

            self.item_buffer.append(item)

            if self.current_item == self.config['buffer']:
                self.current_item = 0
                return self.insert_item(self.item_buffer, spider)

            else:
                return item

        return self.insert_item(item, spider)

    def close_spider(self, spider):
        """ Method called when the spider is closed
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: None
        """
        if self.item_buffer:
            self.insert_item(self.item_buffer, spider)

    def insert_item(self, item, spider):
        """ Process the item and add it to MongoDB
        :type item: (Item object) or [(Item object)]
        :param item: The item(s) to put into MongoDB
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: Item object
        """
        if not isinstance(item, list):
            item = dict(item)

            if self.config['append_timestamp']:
                item['scrapy-mongodb'] = {'ts': datetime.datetime.utcnow()}

        if self.config['unique_key'] is None:
            try:
                self.collection.insert(item, continue_on_error=True)
                logger.debug(
                        u'Stored item(s) in MongoDB {0}/{1}'.format(
                                self.config['database'], self.config['collection'])
                )
            except errors.DuplicateKeyError:
                logger.debug(u'Duplicate key found')
                if self.stop_on_duplicate > 0:
                    self.duplicate_key_count += 1
                    if self.duplicate_key_count >= self.stop_on_duplicate:
                        self.crawler.engine.close_spider(
                                spider,
                                'Number of duplicate key insertion exceeded'
                        )
                pass

        else:
            key = {}
            if isinstance(self.config['unique_key'], list):
                for k in dict(self.config['unique_key']).keys():
                    key[k] = item[k]
            else:
                key[self.config['unique_key']] = item[self.config['unique_key']]

            self.collection.update(key, item, upsert=True)

            logger.debug(
                    u'Stored item(s) in MongoDB {0}/{1}'.format(
                            self.config['database'], self.config['collection'])
            )

        return item
