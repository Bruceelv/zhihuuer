# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider,Request
import json
from zhihuuer.items import UserItem

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'zhi-mu-qing-yang'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit=20'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    #整个程序开始运行的入口，调用下面两个方法，实现死循环
    def start_requests(self):
        #分析用户详情
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query),callback=self.parse)
        #分析用户关注详情：调用上面这个获取用户详情，调用自己获取所有关注用户
        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0),callback=self.parse_followers)

    #独立的模块，分析用户详情
    def parse(self, response):
        result = json.loads(response.text)  # 返回的json格式进行加载转码
        item = UserItem()
        for field in item.fields:  # 对items.py里面定义的变量字段进行遍历
            if field in result.keys():  # 如果改变量字段在返回的json格式的键里面，则赋值
                item[field] = result.get(field)
        yield item
        yield Request(self.followers_url.format(user=result.get('url_token'), include=self.followers_query, offset=0),callback=self.parse_followers)

    def parse_followers(self, response):
        results = json.loads(response.text)

        #获取用户详情
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query), callback=self.parse)
                # yield Request(self.followers_url.format(user=result.get('url_token'), include=self.followers_query,offset=0),callback=self.parse_followers)

        #获取下一页url
        if 'paging' in results.keys() and not results.get('paging').get('is_end'):
            next_page = results.get('paging').get('next')
            yield  Request(next_page, self.parse_followers)


