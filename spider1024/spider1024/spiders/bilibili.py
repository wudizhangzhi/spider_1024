# -*- coding:utf8 -*-

import re
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lxml import etree
from spider1024.items import BiliVideoItem, BiliTag
import requests
import time
import json
# import logging

class BiLiSpider(CrawlSpider):
    name = 'bilibili'
    allowed_domains = ['bilibili.com']
    start_urls = [
        'http://www.bilibili.com/',
        'http://www.bilibili.com/video/av10136337/',
        'http://space.bilibili.com/32820037/',
    ]
    rules = [
        Rule(LinkExtractor(allow=('http://www.bilibili.com/[a-z]+/[a-z0-9\-\_]+\.html', )), follow=True),
        Rule(LinkExtractor(allow=('/?video/av[0-9]+/$', )), callback='parse_videoitem', follow=True),
        Rule(LinkExtractor(allow=('www.bilibili.com/video/av[0-9]+/$', )), callback='parse_videoitem', follow=True),
        Rule(LinkExtractor(allow=('bangumi.bilibili.com/[a-z0-9]*',)), , follow=True),
        Rule(LinkExtractor(allow=('http://space.bilibili.com/[0-9]+/?', )), follow=True),

    ]
    # def parse(self, response):
    #     url = response.url
    #     c = re.compile(r'http://www.bilibili.com/video/av[0-9]+/')
    #     group = c.match(url)
    #     if group:
    #         self.parse_item(response)
    def parse_videoitem(self, response):
        item = BiliVideoItem()
        url = response.url
        try:
            aid = re.findall(r'video/av(\d+)/', url)
            if not aid:
                print '没有aid:%s' % url
                pass
            else:
                aid = aid[0]
                title = response.xpath('//div[@class="v-title"]/h1/@title').extract()[0].strip()
                mid = response.xpath('//div[@id="r-info-rank"]/a/@mid').extract()[0].strip()
                # 上传时间
                createtime = response.xpath('//time[@itemprop="startDate"]/@datetime').extract()[0].strip()
                # 描述
                vdesc_list = response.xpath('//div[@id="v_desc"]/text()').extract()
                vdesc = ''.join(vdesc_list)
                # 访问视频接口获取视频数据
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
                item['title'] = title
                item['mid'] = mid
                item['url'] = url
                item['createtime'] = createtime
                item['vdesc'] = vdesc
                # TODO 获取标签
                yield item
                # # 获取标签
                # try:
                #     url_tag = 'http://api.bilibili.com/x/tag/archive/tags?aid=%s&jsonp=jsonp&_=%s' % (aid, int(time.time()*1000))
                #     r = requests.get(url_tag, timeout=10)
                #     j = json.load(r.text)
                #     for tag in j['data']:
                #         item = BiliTag()
                #         item['name'] = tag['name']
                #         item['tag_id'] = tag['tag_id']
                #         item['typeid'] = tag['typeid']
                #         item['ctime'] = tag['ctime']
                #         item['use'] = tag['use']
                #         item['atten'] = tag['atten']
                #         item['is_atten'] = tag['is_atten']
                #         item['likes'] = tag['likes']
                #         item['hates'] = tag['hates']
                #         item['attribute'] = tag['attribute']
                #         item['liked'] = tag['liked']
                #         item['hated'] = tag['hated']
                #         yield item
                # except Exception, e:
                #     print e
        except Exception, e:
            print '=======\n %s' % e
            # logging(e)



    def parse_uperitem(self, response):
        mid = re.findall(r'http?://space.bilibili.com/(\d+)', response.url)
        if not mid:
            pass
        else:
            mid = mid[0]
            #使用ajax获取数据
            url_uper_video = 'http://space.bilibili.com/ajax/member/getSubmitVideos?mid=%s&page=1&pagesize=25&_=%s' % (mid, int(time.time()*1000))
            r = requests.get(url_uper_video, timeout=10)
            try:
                j = json.loads(r.text)
                vlist = j['data']['vlist']
                for video in vlist:
                    videoItem = BiliVideoItem()
                    videoItem['url'] = response.url
                    videoItem['upper_id'] = mid
                    # videoItem['title'] = video['title']
                    videoItem['cover'] = video['pic']
                    print u'start download :%s' % video['pic']
                    yield videoItem
            except Exception, e:
                print '没有数据:%s' % url_uper_video
                print e
