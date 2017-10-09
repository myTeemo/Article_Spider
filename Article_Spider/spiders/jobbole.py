# -*- coding: utf-8 -*-
import re
import datetime

import scrapy

from urllib import parse

from scrapy.http import Request
from scrapy.loader import ItemLoader

from Article_Spider.items import JobBoleArticleItem
from Article_Spider.items import JobBoleArticleLoader
from Article_Spider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["blog.jobbole.com"]
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中具体文章url,并交给指定方法解析字段
        2. 获取下一页url,并交给scrapy下载
        :param response:
        :return:
        """

        # 获取下一页url
        post_nodes = response.css('#archive .post.floated-thumb .post-thumb a')
        for post_node in post_nodes:
            post_url = post_node.css('::attr(href)').extract_first('')
            image_url = post_node.css('img::attr(src)').extract_first('')
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url}, callback=self.parse_detail)

        next_page = response.css('a.next.page-numbers::attr(href)').extract_first('')
        if next_page:
            yield Request(url=parse.urljoin(response.url, next_page), callback=self.parse)

    def parse_detail(self, response):
        front_image_url = response.meta.get('front_image_url', '')

        item_loader = JobBoleArticleLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('praise_nums', '.post-adds span.vote-post-up h10::text')
        item_loader.add_css('fav_nums', '.post-adds span.bookmark-btn::text')
        item_loader.add_css('comment_nums', '.post-adds a[href="#article-comment"] span::text')
        item_loader.add_css('content','.entry')
        item_loader.add_css('tags', '.entry-meta-hide-on-mobile a::text')

        article_item = item_loader.load_item()

        yield article_item

