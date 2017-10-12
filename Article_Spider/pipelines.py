# -*- coding: utf-8 -*-
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticleSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '123456', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article_details(title, create_date, url, url_object_id, front_image_url, front_image_path,
                                        comment_nums, fav_nums, praise_nums, tags, content)
                                        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item['title'], item['create_date'], item['url'], item['url_object_id'],
                                         item['front_image_url'][0], item['front_image_path'], item['comment_nums'],
                                         item['fav_nums'], item['praise_nums'], item['tags'], item['content']))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)

    def do_insert(self, cursor, item):
        if item['front_image_path']:
            insert_sql = """
                       insert into article_details(title, create_date, url, url_object_id, front_image_url, front_image_path,
                                                   comment_nums, fav_nums, praise_nums, tags, content)
                                                   values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   """
            cursor.execute(insert_sql, (item['title'], item['create_date'], item['url'], item['url_object_id'],
                                             item['front_image_url'][0], item['front_image_path'], item['comment_nums'],
                                             item['fav_nums'], item['praise_nums'], item['tags'], item['content']))

    def handle_error(self, failure):
        print(failure)


class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open('articleexpot.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value['path']

            item['front_image_path'] = image_file_path
        else:
            item['front_image_path'] = ''

        return item