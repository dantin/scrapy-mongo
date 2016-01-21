# scrapy-utils

Scrapy的工具库

* scrapy_mongo

    Scrapy爬取结果进MongoDB的Pipeline
    
* scrapy_random_useragent

    动态UserAgent

### 工具

    # 打包
    python setup.py sdist
    # 安装
    pip install dist/scrapy-utils-0.0.1.tar.gz
    # 卸载
    pip uninstall scrapy-utils

### 使用方法

* scrapy_mongo

    在settings.py, 修改ITEM_PIPELINES的设置,如下:
    
        ITEM_PIPELINES = {
            'scrapy_mongo.pipelines.MongoDBPipeline': 300
        }
    
    同时指定MongoDB的uri, database和collection
    
    MONGODB_URI = 'mongodb://10.3.1.241:27017/'
    MONGODB_DATABASE = 'crawler'
    MONGODB_COLLECTION = 'scrapy_items'
    

* scrapy_random_useragent

    在settings.py, 修改DOWNLOADER_MIDDLEWARES的设置,如下:

        DOWNLOADER_MIDDLEWARES = {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_random_useragent.middlewares.RandomUserAgentMiddleware': 1,
        }

    禁用默认的UserAgentMiddleware,启用自有的 RandomUserAgentMiddleware

    若需使用自定义的UserAgent,增加USER_AGENT_LIST设置,定义自己的UserAgent

        USER_AGENT_LIST = "/path/to/useragents.txt"
