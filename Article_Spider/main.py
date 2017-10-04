# -*- coding: utf-8 -*-
__author__ = "Eilene HE"
__date__ = '2017/10/3 12:58'
import sys
import os

from scrapy.cmdline import execute


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'jobbole'])
