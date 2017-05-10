# -*- coding:utf8 -*-
import requests
import datetime
import time
import torndb
from items import BiliTag
import redis
import json

class Tag():
    def __init__(self):
        self.mysql_cursor = torndb.Connection(
            'localhost', 'demon', user='root')
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
        self.redis_cursor = redis.Redis(connection_pool=pool)

    def saveTag2mysql(self, item):
        aid = item['aid']
        if not self.isTagExists(item):
            tagid = self._savetag(item)
            print 'save new tag success:%s' % aid
        if not self.isVideoTagsaved(item):
            self._saveVideTag(item)
        time.sleep(1)

    def isTagExists(self, item):
        tag_id = item['tag_id']
        sql = 'select * from bilibili_bilitag where `tag_id`=%s'
        return self.mysql_cursor.query(sql, tag_id)

    def _savetag(self, item):
        sql = '''INSERT into
     `bilibili_bilitag`(`name`, `tag_id`, `typeid`, `ctime`, `use`, `atten`
     ,`is_atten`, `likes`, `hates`, `attribute`, `liked`, `hated`, `createtime`)
     values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        self.mysql_cursor.execute(sql, item['name'], item['tag_id'],
                                item['typeid'],
                                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['ctime'])),
                                item['use'],
                                 item['atten'], item['is_atten'], item['likes'],
                                  item['hates'], item['attribute'],
                                  item['liked'], item['hated'], datetime.datetime.now())

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

    def _getAvids(self):
        return self.redis_cursor.lpop('video_aid')

    def crawl(self, aid):
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

    def run(self):
        while True:
            aid = self._getAvids()
            if not aid:
                print 'null :%s' % datetime.datetime.now()
                time.sleep(10)
            else:
                print 'start :%s' % aid
                self.crawl(aid)

if __name__ == '__main__':
    t = Tag()
    t.run()
    # item = {'tag_id': 760681}
    # print t.isTagExists(item)
