from monster_siren.items import MonsterSirenItem
from jsonpath import jsonpath
import scrapy
import json


class SongsSpider(scrapy.Spider):
    name = 'songs'
    allowed_domains = ['hypergryph.com', 'hycdn.cn']
    start_urls = ['https://monster-siren.hypergryph.com/api/songs']
    music_name = {}
    source = {}
    lyric = {}

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
        cid = jsonpath(cache, '$..cid')[0]
        # 以url为键，cid为值储存，方便查询链接对应的cid
        self.lyric[lyric_url] = cid
        self.source[source_url] = cid
        # 以cid为键，歌曲名为值储存，方便查询cid对应的名字
        self.music_name[cid] = name
        # 发送请求，获取音频文件
        yield scrapy.Request(
            url=source_url,
            callback=self.music_mp3
        )
        # 发送请求，获取歌词文件，因为部分歌曲没有歌词所以try一下防止报错
        try:
            yield scrapy.Request(
                url=lyric_url,
                callback=self.lyric_lrc
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
        cid = self.source[response.url]
        name = self.music_name[cid]

        temp = MonsterSirenItem()
        temp['name'] = name
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
        cid = self.lyric[response.url]
        name = self.music_name[cid]

        temp = MonsterSirenItem()
        temp['name'] = name
        temp['source'] = False
        temp['lyric'] = response.body
        temp['suffix'] = 'lrc'
        yield temp
        pass
