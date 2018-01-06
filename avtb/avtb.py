import os

import requests
from lxml import etree

TIMEOUT = 10
HOST = 'http://www.avtb008.com'


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


def download(url, filename):
    dirpath = os.path.dirname(filename)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    if os.path.exists(filename):
        raise Exception('已经存在')
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for content in r.iter_content(1024):
            f.write(content)
            f.flush()
    print('下载成功: {}'.format(filename))


def get_video_download_link(url):
    r = requests.get(url, timeout=TIMEOUT)
    root = etree.HTML(r.text)
    video_link = root.xpath('//source[@type="video/mp4"]/@src')[0]
    title = root.xpath('//*[@id="video"]/h1/text()')[0]
    # print(title, video_link)
    return video_link
    # if not dirpath:
    #     dirpath = 'videos'
    # download(video_link, '{dirpath}/{title}.mp4'.format(dirpath=dirpath, title=title))


def get_all_download_link(url):
    generator = get_all_video_from_url(url)
    while True:
        try:
            title, url, thumb = next(generator)
            print(title)
            download_link = get_video_download_link(''.join((HOST, url)))
            with open('result.txt', 'a') as f:
                f.write(download_link + '\n')
        except StopIteration:
            break
    print('结束')


if __name__ == '__main__':
    # videos = get_all_video_from_url('http://www.avtb008.com/guochan/recent/8/')
    # print(type(videos))
    get_all_download_link('http://www.avtb008.com/guochan/recent/30/')
