# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
        name='scrapy-utils',
        version="0.0.1",
        packages=find_packages('src'),
        package_dir={'': 'src'},
        package_data={
            # 任何包中含有.txt文件，都包含它
            '': ['*.txt'],
            # 包含scrapy_random_useragent包,data文件夹中的 *.dat文件
            'scrapy_random_useragent': ['data/*.dat'],
        }
)
