# scrapy-monster-siren
**不建议使用这个项目**\
N年前写的，不规范，效果也不够好，建议转到新项目[crawler-monster-siren](https://github.com/FrothierNine346/crawler-monster-siren)
---
使用scrapy框架爬取塞壬唱片官网所有歌曲和歌词文件\
需要安装以下模块:\
scrapy、jsonpath\
在项目目录(monster_siren)运行:\
scrapy crawl songs\
运行爬虫\
\
2021/8/17\
新增分布式爬虫版\
songs_redis.py\
分布式爬虫需要安装以下模块:\
scrapy_redis\
分布式爬虫需要安装以下应用:\
redis\
运行分布式爬虫需要在settings中取消注释分布式爬虫部分
