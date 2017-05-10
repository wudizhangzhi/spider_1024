# -*- coding:utf8 -*-

from sqlalchemy import Column, String, create_engine, Table, Integer,\
                    Text, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import chardet

# 创建对象的基类:
Base = declarative_base()

# class ORMBase(Base):
#     def gettext(self, text):
#         return text[:10]

class Video(Base):
    __tablename__ = 'video'

    id = Column(Integer, primary_key = True)
    aid = Column(Integer)# avid
    mid = Column(Integer) # up主
    url = Column(Text) # url
    title = Column(Text)# 标题
    view = Column(Integer) # 总播放数量
    danmaku = Column(Integer)# 总弹幕数量
    reply = Column(Integer) # 评论数量
    favorite = Column(Integer)# 收藏
    coin = Column(Integer)# 硬币
    share = Column(Integer)# 分享

    def __unicode__(self):
        return "<Video %s>" % self.title

    __repr__ = __unicode__

def run():
    # 初始化数据库连接:
    engine = create_engine('mysql+mysqldb://root:@localhost:3306/bili')

    # #绑定元信息
    # metadata = MetaData(engine)
    # #创建数据表，如果数据表存在则忽视！！！
    # metadata.create_all(engine)

    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()
    # # 创建新User对象:
    # new_user = Video(id='1', title='test')
    # # 添加到session:
    # session.add(new_user)
    # 提交即保存到数据库:
    session.commit()
    result = session.query(Video).order_by(Video.id.desc()).first()
    print result
    print result.url

    # 关闭session:
    session.close()

if __name__ == '__main__':
    run()
    import os
    print __file__
    print  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
