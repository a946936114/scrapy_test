# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import DarkAVItem
from ..items import DarkRepliesItem
import sqlite3


class DarkAV(scrapy.Spider):
    name = "dark_av"
    mid = 97177641
    start_urls = [
        "https://space.bilibili.com/ajax/member/getSubmitVideos?mid=97177641&tid=0&keyword=&order=pubdate&page=1"]
    urls_num = "https://space.bilibili.com/ajax/member/getSubmitVideos?mid=97177641&tid=0&keyword=&order=pubdate&page="
    num = 1  # 记录page值，以便翻页
    table = "dark_av"

    def parse(self, response):
        js = json.loads(response.body)
        vlists = js["data"]["vlist"]
        if len(vlists) != 0:
            for vlist in vlists:
                item = DarkAVItem()
                item["aid"] = vlist["aid"]
                item["pic"] = vlist["pic"]
                item["title"] = vlist["title"]
                item["comment"] = vlist["comment"]
                item["created"] = vlist["created"]
                yield item

            self.num = self.num + 1
            next_url = self.urls_num + str(self.num)
            yield scrapy.Request(next_url, callback=self.parse)


class DarkReplies(scrapy.Spider):
    name = "dark_replies"
    table = "dark_replies"
    url_reply = "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&type=1&sort=0&pn={pn}&oid={aid}"
    url_reply_reply = "https://api.bilibili.com/x/v2/reply/reply?jsonp=jsonp&pn={pn}&type=1&oid={aid}&ps=10&root={root}"
    num1 = 1

    def start_requests(self):
        # 连接数据库，读出dark_av爬的AV号
        db_name = self.settings.get("SQLITE_DB_NAME", "scrapy_defaut.db")
        db_conn = sqlite3.connect(db_name)
        db_cur = db_conn.cursor()
        sql = "SELECT aid  FROM dark_av"
        aids = db_cur.execute(sql).fetchall()
        db_conn.close()
        for aid in aids:
            # 这里的format直接传数字也行，不用转字符串
            yield scrapy.Request(self.url_reply.format(pn=1, aid=aid[0]), callback=self.parse_reply,
                                 meta={"aid": aid[0], "pn": 1})

    def parse(self, response):
        pass

    def parse_reply(self, response):
        js = json.loads(response.body)
        # count = js["data"]["page"]["count"]
        # size = js["data"]["page"]["size"]
        # e=(a+(b-1))/b  进一法 大概就是math.ceil()
        replies = js["data"]["replies"]
        if len(replies) != 0:
            for reply in replies:
                item = DarkRepliesItem()
                item["aid"] = reply["oid"]
                item["rpid"] = reply["rpid"]
                item["mid"] = reply["mid"]
                item["uname"] = reply["member"]["uname"]
                item["message"] = reply["content"]["message"]
                item["root"] = reply["root"]
                item["parent"] = reply["parent"]
                item["floor"] = reply["floor"]
                yield item
                if reply["rcount"] > 0:
                    yield scrapy.Request(self.url_reply_reply.format(pn=1, aid=response.meta["aid"],root=reply["rpid"]),
                                         callback=self.parse_reply_reply,
                                         meta={"aid": reply["oid"], "pn": 1,"root": reply["rpid"]})
            yield scrapy.Request(self.url_reply.format(pn=response.meta["pn"] + 1, aid=response.meta["aid"]),
                                 callback=self.parse_reply,
                                 meta={"aid": response.meta["aid"], "pn": response.meta["pn"] + 1})

    def parse_reply_reply(self, response):
        js = json.loads(response.body)
        replies = js["data"]["replies"]
        if len(replies) != 0:
            for reply in replies:
                item = DarkRepliesItem()
                item["aid"] = reply["oid"]
                item["rpid"] = reply["rpid"]
                item["mid"] = reply["mid"]
                item["uname"] = reply["member"]["uname"]
                item["message"] = reply["content"]["message"]
                item["root"] = reply["root"]
                item["parent"] = reply["parent"]
                item["floor"] = reply["floor"]
                yield item
            yield scrapy.Request(self.url_reply_reply.format(pn=response.meta["pn"] + 1, aid=response.meta["aid"],
                                                             root=response.meta["root"]),
                                 callback=self.parse_reply_reply,
                                 meta={"aid": response.meta["aid"], "pn": response.meta["pn"] + 1,
                                       "root": response.meta["root"]})
