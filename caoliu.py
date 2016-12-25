# coding=utf8
__author__ = 'MOON'
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import time
import requests
import multiprocessing
import torndb
from random import choice
from base64 import b64encode
from lxml import etree
import os
import re
import logging
import logging.config
import redis
import chardet

'''
#获取页面的链接
#所有行
lines =  response.xpath('//h3/a[starts-with(@href, "htm_data")]')
for line in lines:
    title = line.xpath('./text()').extract_first() #标题
    href = line.xpath('./@href').extract_first() #内容页面链接
    #TODO 从标题判断内容


#获取下载链接
# regx = re.compile(r'hash=([0-9a-z]+)')
# hashlist = regx.findall(content)
# print set(hashlist)
# link = 'http://www.rmdown.com/link.php?hash=%s' % hashlist[0]
# downloadlink = 'http://www.rmdown.com/download.php?ref=%s&reff=%s&submit=download' % (hash, b64encode(str(int(time.time()))))

'''
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]


def catchKeyboardInterrupt(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except KeyboardInterrupt:
            print '\n[*] 强制退出程序'
            logging.debug('[*] 强制退出程序')

    return wrapper


class CaoLiu(object):
    '''
    爬取列表 -> 内容页面获取下载地址 -> 内容页面获取hash值 -> 保存到数据库 -> 下载
    '''

    def __init__(self):
        self.DEBUG = True
        self.pre = 'caoliu'
        self.session = requests.Session()
        self.TIMEOUT = 5
        self.headers = {
            'User-Agent': choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            # 'Accept-Encoding': 'gzip, deflate'
        }
        self._initDB()

    def _initDB(self):
        self.mysql_cursor = torndb.Connection(host='localhost', user='root', password='admin', database='caoliu')
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
        self.redis_cursor = redis.Redis(pool)

    def _get(self, url, headers=None, data=None, proxy=None):
        _headers = self.headers
        if headers:
            assert isinstance(headers, dict)
            for i in headers.items():
                _headers[i[0]] = i[1]
        return self.session.get(url, headers=_headers, data=data, proxies=proxy, timeout=self.TIMEOUT)

    def _post(self, url, headers=None, data=None, proxy=None):
        _headers = self.headers
        if headers:
            assert isinstance(headers, dict)
            for i in headers.items():
                _headers[i[0]] = i[1]
        return self.session.post(url, headers=_headers, data=data, proxies=proxy, timeout=self.TIMEOUT)

    def findsize(self, title):
        '''
        找到标题中的大小
        :param title:
        :return:
        '''
        m = re.findall(r'\[\w*\/([0-9\.GBMgbm]+)\]', title)
        if m:
            return m[0]
        else:
            return 0

    def findfanhao(self, title):
        '''
        找到番号
        :return:
        '''
        m = re.findall(r'\][- ]*([a-zA-Z0-9\-]+)', title)
        if m:
            if m[0].isdigit():
                return False
            else:
                return m[0].upper()
        else:
            return False

    def findcaption(self, title):
        '''
        是否有字幕
        :return:
        '''
        if u'字幕' in title or u'中文' in title:
            return 1
        else:
            return 0

    def findimg(self, url):
        '''
        找图片
        :param hash:
        :param url:
        :return:
        '''
        try:
            r = self._get(url)
            r.encoding = 'gbk'
            pattern = r'src=\'([^\']+\.(jpg|png))\''
            m = re.findall(pattern, r.text)

        except Exception, e:
            print e
            logging.error(e)

    @classmethod
    def formatsize(cls, size):
        '''
        返回统一单位的大小
        :param size:
        :return:
        '''
        ret = re.split(r'{m|M|mb|MB}', size)
        if len(ret) > 1:  # 单位是M
            return '%0.2f' % (float(ret[0]) / 1024)
        else:
            return re.sub(r'[GBgb]', '', size)

    def save_list(self, title, href, fanhao, size, caption):
        '''
        保存列表
        :param title:
        :param href:
        :param fanhao:
        :param size:
        :param caption:
        :return:
        '''
        try:
            sql = 'insert into caoliu_source(`title`,`url`,`code`,`size`,`caption`) value(%s,%s,%s,%s,%s)'
            self.mysql_cursor.execute(sql, title, href, fanhao, size, caption)
            if self.DEBUG:
                print '保存:%s' % title
        except Exception, e:
            print e
            logging.error(e)

    def scrapylist_onepage(self, url):
        try:
            r = self._get(url)
        except Exception, e:
            print e
            logging.error(e)
            return False
        r.encoding = 'gbk'
        root = etree.HTML(r.text)
        lines = root.xpath('//h3/a[starts-with(@href, "htm_data")]')
        if not lines:
            logging.error('该列表页面找不到内容内容:%s' % url)
        for line in lines:
            try:
                title = line.xpath('./text()')  # 标题
                href = line.xpath('./@href')  # 内容页面链接
                if title and href:
                    title = title[0]
                    href = href[0]
                    # 根据标题获取大小，番号，题目，是否有中文字幕
                    size = self.findsize(title)
                    if size:
                        size = caoliu.formatsize(size)
                    fanhao = self.findfanhao(title)
                    caption = self.findcaption(title)
                    href = 'http://www.t66y.com/' + href
                    print title
                    print fanhao, size, caption, href
                    # 判断是否保存过
                    sql = 'select * from caoliu_source where `url`=%s'
                    ret = self.mysql_cursor.query(sql, href)
                    if ret:
                        print '保存过,title:%s' % title
                    else:
                        self.save_list(title, href, fanhao, size, caption)
            except Exception, e:
                print e
                logging.error(e)

    def scrapycode(self, url):
        '''
        爬区信息页面，获取种子和图片
        :param url:
        :return:
        '''
        r = self._get(url)
        r.encoding = 'gbk'
        regx = re.compile(r'hash=([0-9a-z]+)')
        hashlist = regx.findall(r.text)
        if not hashlist:
            print '没有找到hash'
            try:
                sql = 'update caoliu_source set `hash`=%s where `url`=%s'
                self.mysql_cursor.execute(sql, 'none', url)
            except Exception, e:
                print e
                logging.error(e)
        else:
            hash = hashlist[0]
            # link = 'http://www.rmdown.com/link.php?hash=%s' % hash
            # 更新数据库
            try:
                sql = 'update caoliu_source set `hash`=%s where `url`=%s'
                self.mysql_cursor.execute(sql, hash, url)
            except Exception, e:
                print e
                logging.error(e)

    @classmethod
    def downloadlink(cls, hash):
        '''
        获取实时种子下载链接
        :param hash:
        :return:
        '''
        return 'http://www.rmdown.com/download.php?ref=%s&reff=%s&submit=download' % (
            hash, b64encode(str(int(time.time()))))

    def download(self, hash):
        '''
        下载种子
        :param hash:
        :return:
        '''
        try:
            url = self.downloadlink(hash)
            filepath = 'torrent'
            if not os.path.exists(filepath):
                os.mkdir(filepath)
            r = requests.get(url, stream=True)
            with open(os.path.join(filepath, '%s.torrent' % hash), 'wb') as f:
                for content in r.iter_content(1024):
                    f.write(content)
                    f.flush()
            # 成功后更新数据库
            sql = 'update caoliu_source set `isdownload`=1 where `hash`=%s'
            self.mysql_cursor.execute(sql, hash)
            if self.DEBUG:
                print '下载完成:%s' % hash
        except Exception, e:
            print e
            logging.error(e)

    def thread_download(self):
        # 获取任务
        while True:
            sql = 'select * from caoliu_source where `isdownload`=0 and `hash` is not NULL limit 5'
            ret = self.mysql_cursor.query(sql)
            if not ret:
                time.sleep(10)
            else:
                for i in ret:
                    self.download(i['hash'])
                    time.sleep(1)

    def thread_mission(self):
        '''
        从redis取队列，执行任务
        :return:
        '''
        while True:
            try:
                url = self.redis_cursor.lpop(self.pre + 'urllist')
                if not url:
                    time.sleep(20)
                else:
                    self.scrapylist_onepage(url)
                    time.sleep(10)
            except Exception, e:
                print e
                logging.error(e)

    def thread_scrapylist(self):
        '''
        爬取任务
        :return:
        '''
        # TODO 爬取页数
        maxpage = 1500
        while True:
            try:
                r = self._get('http://www.t66y.com/thread0806.php?fid=15')
                root = etree.HTML(r.text)
                maxpage = root.xpath('.//div[@class="pages"]/a/input/@value')
                if maxpage:
                    maxpage = int(maxpage[0].split('/')[1])
            except Exception, e:
                print e
                logging.error(e)

            url = 'http://www.t66y.com/thread0806.php?fid=15&search=&page=%s'
            for i in xrange(maxpage):
                self.scrapylist_onepage(url % i)
            time.sleep(60*60)

    def thread_scrapycodeauto(self):
        '''
        自动获取hash值进程
        :return:
        '''
        # 取任务
        while True:
            try:
                sql = 'select * from caoliu_source where `hash` is NULL limit 1'
                ret = self.mysql_cursor.query(sql)
                if not ret:
                    print '没有任务'
                else:
                    if self.DEBUG:
                        print '开始任务：%s' % ret[0]
                    try:
                        self.scrapycode(ret[0]['url'])
                    except Exception, e:
                        print e
                        logging.error(e)
            except Exception, e:
                print e
                logging.error(e)
            time.sleep(5)

    def thread_downfilm(self):
        '''
        TODO
        :return:
        '''
        pass

    @catchKeyboardInterrupt
    def run(self):
        threads = {
            'scrapylist': self.thread_scrapylist, # 爬取列表
            'scrapycode': self.thread_scrapycodeauto, # 爬取下载的hash
            'download_torrent': self.thread_download, # 下载种子
        }
        for i in threads.itervalues():
            listenProcess = multiprocessing.Process(target=i)
            listenProcess.start()
        while True:
            time.sleep(3)
        # TODO
        # 开始爬取主列表线程 ->获取信息页面地址
        # 开始爬取信息页面 -> 获取种子hash值
        # 开始信息页面的下载图片
        # 开始种子的下载
        pass


if __name__ == '__main__':
    # CONF_LOG = "caoliu.conf"
    # logging.config.fileConfig(CONF_LOG)   # 采用配置文件
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log/caoliu.log',
                    filemode='w')
    logger = logging.getLogger(__name__)
    import coloredlogs

    coloredlogs.install(level='DEBUG')
    caoliu = CaoLiu()
    # caoliu.scrapylist_onepage('http://www.t66y.com/thread0806.php?fid=15&search=&page=0')
    # print caoliu.findfanhao('[MP4/952M]JUX-343 あなたへ 今�、ゆきこの家に泊まります。 森ななこ【中文字幕】')
    # print caoliu.findcaption('[MP4/952M]JUX-343 あなたへ 今�、ゆきこの家に泊まります。 森ななこ【中文字幕】')
    # print CaoLiu.formatsize(caoliu.findsize('[MP4/952M]JUX-343 あなたへ 今�、ゆきこの家に泊まります。 森ななこ【中文字幕】'))
    # caoliu.scrapycode('http://www.t66y.com/htm_data/15/1612/2171110.html')
    caoliu.run()
