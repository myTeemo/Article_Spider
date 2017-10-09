# -*- coding: utf-8 -*-
import datetime
import re

import scrapy

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.loader.processors import TakeFirst
from scrapy.loader.processors import Join


class ArticleSpiderItem(scrapy.Item):

    pass


def date_convert(value):
    value = value.replace('\r', '').replace('\n', '').replace('·', '').strip()
    try:
        value = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        value = datetime.datetime.now().date()

    return value


def get_nums(value):
    match_re = re.match(r'.*?(\d+).*', value)
    if match_re:
        value = int(match_re.group(1))
    else:
        value = 0
    return value


def remove_comment_tags(value):
    if '评论' in value:
        return ''
    else:
        return value


def return_value(value):
    return value


class JobBoleArticleLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
    )

    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value),
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(',')
    )

    pass