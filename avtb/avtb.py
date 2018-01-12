"""AVTB.

Usage:
  avtb.py [-m MODULE] [-p PAGE] [-n NUM]
  avtb.py (-h | --help)
  avtb.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  -m MODULE --module=MODULE select module [default: guochan].
  -p PAGE --page=PAGE page to be crawl [default: 1].
  -n NUM --num=NUM page count [default: 1].
"""

import os
import re
from docopt import docopt
import requests
import time
from lxml import etree
from user_agent import generate_user_agent

TIMEOUT = 10
HOST = 'http://www.avtb008.com'


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=None, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    if not length:
        length = os.get_terminal_size().columns - len(prefix) - len(suffix) - len(percent) - 15
        assert length > 0
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def get_all_video_from_url(url):
    r = requests.get(url, timeout=TIMEOUT)
    root = etree.HTML(r.text)
    divs = root.xpath('//div[@class="video"]')

    for video_div in divs:
        try:
            title = video_div.xpath('.//span[@class="video-title"]/text()')[0]

            thumb = video_div.xpath('.//div[@class="video-thumb"]/img/@src')[0]

            url = video_div.xpath('.//a/@href')[0]
            # print(title, url, thumb)
            yield title, url, thumb
        except Exception as e:
            print(e)


def download(url, filename=None, printprogress=True):
    '''
    下载文件
    :param url: 
    :param filename: 
    :param printprogress: 
    :return: 
    '''
    # url = re.sub(r'(&e=\d+)', '&e=' + str(int(time.time())), url)
    if not filename:
        match = re.findall(r'mp4/(\d+\.mp4)', url)
        filename = 'videos/' + match[0]
    dirpath = os.path.dirname(filename)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    if os.path.exists(filename):
        raise Exception('已经存在: {}'.format(filename))
    headers = {'User-Agent': generate_user_agent(os=('mac', 'linux'))}
    r = requests.get(url, headers=headers, stream=True)
    content_length = int(r.headers.get('Content-Length'))
    assert content_length > 1048576  # 1024 * 1024
    print('开始下载, 文件名: {} 文件大小: {:0.1f}M'.format(filename, float(content_length) / 1024 / 1204))
    downloaded = 0
    with open(filename, 'wb') as f:
        try:
            for content in r.iter_content(1024):
                f.write(content)
                downloaded += len(content)
                if printprogress:
                    # 打印下载进度
                    printProgressBar(downloaded, content_length, prefix='下载进度:', suffix='完成')
                f.flush()
        except Exception as e:
            print(e)
    if downloaded == content_length:
        print('下载成功: {}'.format(filename))
    else:
        print('下载不完整: {}'.format(filename))
        if downloaded < 1048576:
            os.remove(filename)


def get_video_download_link(url):
    r = requests.get(url, timeout=TIMEOUT)
    root = etree.HTML(r.text)
    video_link = root.xpath('//source[@type="video/mp4"]/@src')[0]
    # title = root.xpath('//*[@id="video"]/h1/text()')[0]
    # print(title, video_link)
    return video_link


def get_all_download_link(url):
    # generator = get_all_video_from_url(url)
    # while True:
    #     try:
    #         title, url, thumb = next(generator)
    #         print(title)
    #         try:
    #             download_link = get_video_download_link(''.join((HOST, url)))
    #             # with open('result.txt', 'a') as f:
    #             #     f.write(download_link + '\n')
    #         except Exception as e:
    #             print(e)
    #     except StopIteration:
    #         break
    for title, url, thumb in get_all_video_from_url(url):
        download_link = get_video_download_link(''.join((HOST, url)))
        yield download_link
    print('结束')


def main(**kwargs):
    _module = kwargs.get('module', None)
    page = int(kwargs.get('page', 1) or 1)
    num = int(kwargs.get('num', 1) or 1)
    if not _module:
        _module = 'guochan'

    # 爬取每一页
    url = 'http://www.avtb008.com/{module}/{page}/'
    for page in range(page, page + num):
        # 下载每一个
        if page == 1:
            page = ''
        else:
            page = 'recent/{}/'.format(page)
        for title, url, thumb in get_all_video_from_url(url.format(module=_module, page=page)):
            try:
                download_link = get_video_download_link(''.join((HOST, url)))
                download(download_link, 'videos/{}.mp4'.format(title))
            except Exception as e:
                print(e)


if __name__ == '__main__':
    # url = 'http://www.avtb008.com/guochan'
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    main(**{k.replace('--', ''): v for k, v in arguments.items()})
