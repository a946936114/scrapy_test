import scrapy
import json
from ..items import DarkAVItem
import sqlite3


class DarkAV(scrapy.Spider):
    name = "dark_av"
    mid = 97177641
    start_urls = [
        "https://space.bilibili.com/ajax/member/getSubmitVideos?mid=97177641&tid=0&keyword=&order=pubdate&page=1"]
    urls_num = "https://space.bilibili.com/ajax/member/getSubmitVideos?mid=97177641&tid=0&keyword=&order=pubdate&page="
    num = 1
    table = "dark_av"

    def parse(self, response):
        js = json.loads(response.body)
        vlists = js["data"]["vlist"]
        for vlist in vlists:
            item = DarkAVItem()
            item["aid"] = vlist["aid"]
            item["pic"] = vlist["pic"]
            item["title"] = vlist["title"]
            item["comment"] = vlist["comment"]
            item["created"] = vlist["created"]
            yield item
        if len(vlists) != 0:
            self.num = self.num + 1
            next_url = self.urls_num + str(self.num)
            yield scrapy.Request(next_url, callback=self.parse)


class DarkReplies(scrapy.Spider):
    name = "dark_replies"
    table = "dark_replies"
    url_aid = "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&type=1&sort=0&pn=1&oid="
    url_pn = "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&type=1&sort=0&pn=1&oid="
    num1 = 1

    def start_requests(self):
        db_name = self.settings.get("SQLITE_DB_NAME", "scrapy_defaut.db")
        db_conn = sqlite3.connect(db_name)
        db_cur = db_conn.cursor()
        db_conn.close()
        sql = "SELECT aid  FROM dark_av"
        aids=db_cur.execute(sql)
        for aid in aids:
            yield scrapy.Request(self.urls_num1+str(aid),callback=self.request_reply)

    def parse(self, response):
        pass

    def request_reply(self, response):
        js = json.loads(response.body)
        count=js["data"]["page"]["count"]
        size=js["data"]["page"]["size"]
        for pn in range(1,((count+(size-1))//size)+1):
            yield scrapy.Request(self.urls_num1+str(pn),callback=self.request_reply)