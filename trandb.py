# -*- coding:utf8 -*-
import torndb

mysql_cursor = torndb.Connection('localhost', 'bili', user='root')
cursor = torndb.Connection('localhost', 'demon', user='root')
data = mysql_cursor.query('select * from `video`')
sql = 'insert into `bilibili_bilivideo`(`aid`,`mid`,`url`,`title`,`view`,`danmaku`,\
`reply`,`favorite`,`coin`,`share`) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
for index in xrange(0, len(data), 100):
    params = [(i['aid'], i['mid'], i['url'],
    i['title'], i['view'], i['danmaku'],
    i['reply'], i['favorite'],
    i['coin'], i['share']) for i in data[index: index + 100]]
    cursor.executemany(sql, params)
    print 'down:%s' % (float(index)/len(data))
