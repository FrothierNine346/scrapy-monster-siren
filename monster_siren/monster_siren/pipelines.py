# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class MonsterSirenPipeline:

    def process_item(self, item, spider):
        """
        接受数据并保存
        OSError: [WinError 123] 文件名、目录名或卷标语法不正确。: 'music/0:00:01'
        :param item:
        :param spider:
        :return:
        """
        name = item['name']
        source = item['source']
        lyric = item['lyric']
        suffix = item['suffix']
        # 部分歌曲名有非法字符，此处替换
        name = re.sub(r'[\\/:*?<>"|]', '!', name)
        # 部分歌曲名带有下面第一个标签，这是对应歌曲的无人声版，所以我把它放到有人声版的同一文件夹，但鹰角把部分标签写错成了后两种，目前正则无法
        # 匹配到最后一种，有大佬的话帮忙写个能同时匹配下面三种的正则
        # (Instrumental)
        # (instrumental)
        # （Instrumenta）
        instrumental = re.search(r'(.*) \(Instrumental\)?', name, re.I)
        if not os.path.exists('music'):
            os.mkdir('music')
        if instrumental:
            if not os.path.exists('music/{}'.format(instrumental.group(1))):
                os.mkdir('music/{}'.format(instrumental.group(1)))
            path_mp3 = 'music/{}/{}.{}'.format(instrumental.group(1), name, suffix)
        else:
            if not os.path.exists('music/{}'.format(name)):
                os.mkdir('music/{}'.format(name))
            path_mp3 = 'music/{}/{}.{}'.format(name, name, suffix)
        if source is False:
            data = lyric
        else:
            data = source
        with open(path_mp3, 'wb') as fq:
            fq.write(data)
        return item
