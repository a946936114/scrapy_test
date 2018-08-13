# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3


class ExamplePipeline(object):
    def process_item(self, item, spider):
        return item


class SQLitePipeline(object):
    def __init__(self):
        self.db_conn = None
        self.db_cur = None

    def open_spider(self, spider):
        db_name = spider.settings.get("SQLITE_DB_NAME", "scrapy_defaut.db")
        self.db_conn = sqlite3.connect(db_name)
        self.db_cur = self.db_conn.cursor()

    def close_spider(self, spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self, item, spider):
        self.insert_db(item,spider.table)
        return item

    def insert_db(self, item,table):
        # bug 数据有引号会解析失败
        # sql = 'INSERT INTO books (' + ','.join(item.keys()) + ") VALUES (\'" + '\',\''.join() + "'" + ')'
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(table, ",".join(item.keys()), ",".join("?" * len(item)))
        self.db_cur.execute(sql, item.values())

        # 每插入一条就commit一次会影响效率
        self.db_conn.commit()
