# -*- coding: utf-8 -*-
import logging
import os
import random

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware(UserAgentMiddleware):
    DEFAULT_USER_AGENT = os.path.normpath(os.path.dirname(__file__) + '/data/user_agent.dat')

    def __init__(self, settings, user_agent='Scrapy'):
        super(RandomUserAgentMiddleware, self).__init__()
        self.user_agent = user_agent
        user_agent_list_file = settings.get('USER_AGENT_LIST')

        if not user_agent_list_file:
            # If USER_AGENT_LIST_FILE settings is not set,
            # Use the default UserAgent from 'data/user_agent.dat'
            logger.info('use agent file: %s', self.DEFAULT_USER_AGENT)
            with open(self.DEFAULT_USER_AGENT, 'r') as f:
                self.user_agent_list = [line.strip() for line in f.readlines()]
        else:
            logger.info('use agent file: %s', user_agent_list_file)

            with open(user_agent_list_file, 'r') as f:
                self.user_agent_list = [line.strip() for line in f.readlines()]

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)
        crawler.signals.connect(
                obj.spider_opened,
                signal=signals.spider_opened)
        return obj

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)
