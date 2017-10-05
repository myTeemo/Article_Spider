# -*- coding: utf-8 -*-
import re
import datetime

import scrapy

from urllib import parse

from scrapy.http import Request

from Article_Spider.items import JobBoleArticleItem
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
        article_item = JobBoleArticleItem()

        front_image_url = response.meta.get('front_image_url', '')
        title = response.css('.entry-header h1::text').extract_first()
        create_date = response.css('.entry-meta-hide-on-mobile::text').extract_first().replace('\r', '')\
                                                                                    .replace('\n', '')\
                                                                                    .replace('·', '')\
                                                                                    .strip()
        praise_nums = int(response.css('.post-adds span.vote-post-up h10::text').extract_first())

        fav_nums = response.css('.post-adds span.bookmark-btn::text').extract_first()
        match_re = re.match(r'.*?(\d+).*', fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0

        comment_nums = response.css('.post-adds a[href="#article-comment"] span::text').extract_first()
        match_re = re.match(r'.*?(\d+).*', comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        content = response.css('.entry').extract_first()

        tag_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ",".join(tag_list)

        article_item['front_image_url'] = [front_image_url]
        article_item['title'] = title
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d")
        except Exception as e:
            create_date = datetime.datetime.now().date()

        article_item['create_date'] = create_date
        article_item['url'] = response.url
        article_item['praise_nums'] = praise_nums
        article_item['fav_nums'] = fav_nums
        article_item['comment_nums'] = comment_nums
        article_item['content'] = content
        article_item['tags'] = tags
        article_item['url_object_id'] = get_md5(response.url)

        yield article_item

