# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.exceptions import DropItem


class BiliVideoItem(scrapy.Item):
    # define the fields for your item here like:
    aid = scrapy.Field()# avid
    mid = scrapy.Field() # up主
    url = scrapy.Field() # url
    title = scrapy.Field()# 标题
    view = scrapy.Field() # 总播放数量
    danmaku = scrapy.Field()# 总弹幕数量
    reply = scrapy.Field() # 评论数量
    favorite = scrapy.Field()# 收藏
    coin = scrapy.Field()# 硬币
    share = scrapy.Field()# 分享
    createtime = scrapy.Field()
    vdesc = scrapy.Field()
    createtime = scrapy.Field()
    vdesc = scrapy.Field()
    # cover = scrapy.Field()# 封面
    # cover_localpath = scrapy.Field()# 封面保存路径

class BiliTag(scrapy.Item):
    aid = scrapy.Field() #avid
    name = scrapy.Field() #
    tag_id = scrapy.Field() #
    typeid = scrapy.Field() #
    ctime = scrapy.Field() #
    use = scrapy.Field() #
    atten = scrapy.Field() #
    is_atten = scrapy.Field() #
    likes = scrapy.Field() #
    hates = scrapy.Field() #
    attribute = scrapy.Field()#
    liked = scrapy.Field()#
    hated = scrapy.Field()#

class BiliUperItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()# up主昵称
    describe = scrapy.Field()# 简介
    contribution = scrapy.Field()# 投稿
    fans = scrapy.Field()# 粉丝
    total_play = scrapy.Field()# 播放数量
    total_video = scrapy.Field()# 视频数量
    uid = scrapy.Field()# uid
    sign_date = scrapy.Field()# 注册时间
    address = scrapy.Field()# 地址
