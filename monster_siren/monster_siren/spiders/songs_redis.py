"""
改造为分布式爬虫步骤:
1.注释掉 allowed_domains、start_urls
2.添加导入 from scrapy_redis.spiders import RedisSpider
3.设置 redis_key
4.更改类继承为 RedisSpider
5.复制__init__方法并设置 self.allowed_domains = list(filter(None, domain.split(',')))
6.在settings设置分布式爬虫部分
可选(必要):
1.以上面方法改造完运行会报一个warning，是调用了一个即将弃用的函数
2.修复warning需要添加导入 from scrapy_redis.utils import bytes_to_str
3.重写 make_request_from_data 方法，如下
"""
from scrapy_redis.utils import bytes_to_str
from scrapy_redis.spiders import RedisSpider
from monster_siren.items import MonsterSirenItem
from jsonpath import jsonpath
import scrapy
import json


class SongsSpider(RedisSpider):
    """
    改造为分布式爬虫
    redis启动命令:
    redis-server
    redis连接命令:
    redis-cli -h 127.0.0.1 -p 6379
    运行爬虫(在爬虫文件目录):
    scrapy runspider <文件名>.py
    redis写入开始链接:
    lpush <redis_key> https://monster-siren.hypergryph.com/api/songs
    """
    name = 'songs-redis'
    redis_key = 'songs'

    # allowed_domains = ['hypergryph.com', 'hycdn.cn']
    # start_urls = ['https://monster-siren.hypergryph.com/api/songs']

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = list(filter(None, domain.split(',')))
        super(SongsSpider, self).__init__(*args, **kwargs)

    def make_request_from_data(self, data):
        url = bytes_to_str(data, self.redis_encoding)
        return scrapy.Request(url, dont_filter=True)

    def parse(self, response):
        """
        获取所有歌曲cid并拼接成链接发送
        :param response:
        :return:
        """
        link_id = jsonpath(json.loads(response.text), '$..cid')
        for link in link_id:
            url = 'https://monster-siren.hypergryph.com/api/song/' + link
            yield scrapy.Request(
                url=url,
                callback=self.music_url
            )
        pass

    def music_url(self, response):
        """
        解析链接内容获取歌曲名、歌词文件url、音频文件url
        :param response:
        :return:
        """
        cache = json.loads(response.text)
        lyric_url = jsonpath(cache, '$..lyricUrl')[0]
        source_url = jsonpath(cache, '$..sourceUrl')[0]
        name = jsonpath(cache, '$..name')[0]
        # 发送请求，获取音频文件
        yield scrapy.Request(
            url=source_url,
            callback=self.music_mp3,
            meta={'name': name}
        )
        # 发送请求，获取歌词文件，因为部分歌曲没有歌词所以try一下防止报错
        try:
            yield scrapy.Request(
                url=lyric_url,
                callback=self.lyric_lrc,
                meta={'name': name}
            )
        except:
            pass
        pass

    def music_mp3(self, response):
        """
        解析数据，发送给pipelines.py处理
        :param response:
        :return:
        """
        temp = MonsterSirenItem()
        temp['name'] = response.meta['name']
        temp['source'] = response.body
        temp['lyric'] = False
        temp['suffix'] = 'mp3'
        yield temp
        pass

    def lyric_lrc(self, response):
        """
        解析数据，发送给pipelines.py处理
        :param response:
        :return:
        """
        temp = MonsterSirenItem()
        temp['name'] = response.meta['name']
        temp['source'] = False
        temp['lyric'] = response.body
        temp['suffix'] = 'lrc'
        yield temp
        pass
