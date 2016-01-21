# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.0.1'

setup(
        name='scrapy-utils',
        author='david_ding',
        author_email='chengjie.ding@gmail.com',
        version=version,
        packages=find_packages('src'),
        package_dir={'': 'src'},
        package_data={
            # 任何包中含有.txt文件，都包含它
            '': ['*.txt'],
            # 包含scrapy_random_useragent包,data文件夹中的 *.dat文件
            'scrapy_random_useragent': ['data/*.dat'],
        },
        install_requires=['pymongo>=3.2', 'Scrapy>=1.0.4'],
)
