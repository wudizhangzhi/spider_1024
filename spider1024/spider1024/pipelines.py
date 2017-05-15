# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from items import *
import scrapy
import torndb
import datetime
import pymongo
import time
import requests
import json
import redis

class Spider1024Pipeline(object):
    def process_item(self, item, spider):
        return item


class DownLoadImgPipeline(ImagesPipeline):
    '''
    下载图片管道
    '''
    def get_media_requests(self, item, info):
        print u'开始下载：%s' % item['cover']
        yield scrapy.Request(item['cover'])

    '''
    [(True,
      {'checksum': '2b00042f7481c7b056c4b410d28f33cf',
       'path': 'full/7d97e98f8af710c7e7fe703abc8f639e0ee507c4.jpg',
       'url': 'http://www.example.com/images/product1.jpg'}),
     (True,
      {'checksum': 'b9628c4ab9b595f72f280b90c4fd093d',
       'path': 'full/1ca5879492b8fd606df1964ea3c1e2f4520f076f.jpg',
       'url': 'http://www.example.com/images/product2.jpg'}),
     (False,
      Failure(...))]
    '''
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['cover_localpath'] = image_paths
        return item


class SaveItemPipeline(object):
    def __init__(self, *args, **kwargs):
        super(SaveItemPipeline, self).__init__(*args, **kwargs)
        self.clinet = pymongo.MongoClient("localhost", 27017)
        self.db = self.clinet["bili"]
        self.mysql_cursor = torndb.Connection('localhost', 'demon', user='root')
        # pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
        # self.redis_cursor = redis.Redis(connection_pool=pool)

    def process_item(self, item, spider):
        # 爬取uper
        self.crawlUser(item['mid'])
        # 保存视频
        self.handlerVideo(item)
        # 爬取tag
        self.crawlTag(item['aid'])
        return item

    def handlerVideo(self, item):
        #判断是否保存过
        if not self.isVideoExisted(item['aid']):
            self.saveVideo(item)
        self.addVideoData(item)

    def isVideoExisted(self, aid):
        sql = 'select * from `bilibili_bilivideo` where `aid`=%s'
        return self.mysql_cursor.query(sql, aid)

    def addVideoData(self, item):
        sql = """
            INSERT into `bilibili_bilivideodata`(`video_id`,`view`,`danmaku`,
            `reply`,`favorite`,`coin`,`share`,`createtime`)
            values(%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.mysql_cursor.execute(sql, item['aid'], item['view'], item['danmaku'],
        item['reply'], item['favorite'], item['coin'], item['share'], datetime.datetime.now())

    def saveVideo(self, item):
        sql = 'insert into `bilibili_bilivideo`(`aid`,`uper_id`,`url`,`title`\
        , `createtime`, `addtime`, `vdesc`)\
         values(%s,%s,%s,%s,%s,%s,%s)'
        self.mysql_cursor.execute(sql, item['aid'], item['mid'], item['url'],
                                    item['title'], item['createtime'],
                                    datetime.datetime.now(), item['vdesc'])

    def pushRedisQueue(self, aid):
        self.redis_cursor.rpush('video_aid', aid)

    def getVideoId(self, aid):
        sql = 'select * from bilibili_bilivideo where `aid`=%s'
        ret = self.mysql_cursor.query(sql, aid)
        if ret:
            return ret[0]['id']
        return False

    def saveTag2mysql(self, item):
        aid = item['aid']
        if not self.isTagExists(item):
            tagid = self._savetag(item)
            print 'save new tag success:%s' % aid
        self.saveTagdata(item)
        if not self.isVideoTagsaved(item):
            self._saveVideTag(item)
        time.sleep(1)

    def saveTagdata(self, item):
        sql = """
            INSERT into `bilibili_bilitagdata`(`tag_id`,`use`,`atten`,
            `is_atten`,`likes`,`hates`,`attribute`,`liked`,`hated`,`createtime`)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.mysql_cursor.execute(sql, item['tag_id'], item['use'],
        item['atten'], item['is_atten'], item['likes'], item['hates'],
        item['attribute'], item['liked'], item['hated'], datetime.datetime.now())

    def isTagExists(self, item):
        tag_id = item['tag_id']
        sql = 'select * from bilibili_bilitag where `tag_id`=%s'
        return self.mysql_cursor.query(sql, tag_id)

    def _savetag(self, item):
        sql = '''INSERT into
         `bilibili_bilitag`(`name`, `tag_id`, `typeid`, `ctime`,`createtime`)
         values(%s,%s,%s,%s,%s)'''
        self.mysql_cursor.execute(sql, item['name'], item['tag_id'],
                                item['typeid'],
                                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['ctime'])),
                                datetime.datetime.now())

    def isVideoTagsaved(self, item):
        sql = 'select * from `bilibili_bilivideotag` where \
        `tag_id`=%s and `video_id`=%s'
        return self.mysql_cursor.query(sql, item['tag_id'], item['aid'])

    def _saveVideTag(self, item):
        # video_id = self.getVideoId(item['aid'])
        try:
            sql = 'insert into `bilibili_bilivideotag`(`video_id`, \
            `tag_id`) values(%s,%s)'
            self.mysql_cursor.execute(sql, item['aid'], item['tag_id'])
        except Exception, e:
            print e
            print item['aid'], item['tag_id']

    def crawlTag(self, aid):
        try:
            url_tag = 'http://api.bilibili.com/x/tag/archive/tags?aid=%s&jsonp=jsonp&_=%s' % (
                aid, int(time.time() * 1000))
            r = requests.get(url_tag, timeout=10)
            j = json.loads(r.text)
            if j['code'] !=0:
                print j
            else:
                for tag in j['data']:
                    item = BiliTag()
                    item['aid'] = aid
                    item['name'] = tag['tag_name']
                    item['tag_id'] = tag['tag_id']
                    item['typeid'] = tag['type']
                    item['ctime'] = tag['ctime']
                    item['use'] = tag['count']['use']
                    item['atten'] = tag['count']['atten']
                    item['is_atten'] = tag['is_atten']
                    item['likes'] = tag['likes']
                    item['hates'] = tag['hates']
                    item['attribute'] = tag['attribute']
                    item['liked'] = tag['liked']
                    item['hated'] = tag['hated']
                    self.saveTag2mysql(item)
        except Exception, e:
            print e

    def UperExists(self, uid):
        sql = 'select * from bilibili_biliuper where uid=%s'
        return self.mysql_cursor.query(sql, uid)

    def crawlUser(self, uid):
        try:
            url_uper = 'http://api.bilibili.com/cardrich?&mid=%s&type=jsonp&_=%s' % (uid, int(time.time()*1000))
            r = requests.get(url_uper, timeout=10)
            j = json.loads(r.text)
            data = j['data']['card']
            if not self.UperExists(uid):
                self.saveUper(data)
                print 'save Upder:%s' % uid
            self.addUperData(data)
            print 'save Uper data:%s' % uid
        except Exception, e:
            print '!!!!!!:%s' % e

    def addUperData(self, data):
        sql = """
            INSERT into `bilibili_biliuperdata`(`uper_id`,`videonum`,`gz`,
            `fans`, `play`,`createtime`) values(%s,%s,%s,%s,%s,%s)
        """
        # self.mysql_cursor.execute(sql, data['mid'], data['videonum'],
        # data['gz'], data['fans'], data['play'])
        #TODO 获取数据
        self.mysql_cursor.execute(sql, data['mid'], 0,
        0, data['fans'], 0, datetime.datetime.now())

    def saveUper(self, data):
        # url_uper = 'http://api.bilibili.com/cardrich?&mid=%s&type=jsonp&_=%s' % (uid, int(time.time()*1000))
        # r = requests.get(url_uper)
        # j = json.loads(r.text)
        # data = j['data']
        sql = """
            INSERT into `bilibili_biliuper`(`name`, `uid`,
            `sign`, `regtime`, `createtime`, `avatar`)
            VALUES(%s,%s,%s,%s,%s,%s)
        """
        self.mysql_cursor.execute(sql, data['name'], data['mid'],
        data['sign'],
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['regtime'])),
        datetime.datetime.now(), data['face'])

    def crawlVideo(self, aid):
        # 访问视频接口获取视频数据
        item = dict()
        url_videdata = 'http://api.bilibili.com/archive_stat/stat?aid=%s&type=jsonp&_=%s' % (aid, int(time.time()*1000))
        r = requests.get(url_videdata, timeout=5)
        j = json.loads(r.text)
        data = j['data']
        item['view'] = data['view']
        item['danmaku'] = data['danmaku']
        item['reply'] = data['reply']
        item['favorite'] = data['favorite']
        item['coin'] = data['coin']
        item['share'] = data['share']
        item['aid'] = aid
        self.addVideoData(item)
