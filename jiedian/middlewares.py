# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from fake_useragent import UserAgent
import requests
import redis
import random
import json
import time


class JiedianSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MyAgent(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = UserAgent().random
        # ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'
        if ua:
            print(ua, '----------------------user_agent chosed-------------------')
            # request.headers.setdefault('Host', 'www.dianping.com')
            request.headers.setdefault('User-Agent', ua)


class ProxyMiddleWare(object):
    r = None
    api_hold = '_api_hold_'
    proxy_key_finish = '_proxy_key_finish_'
    z_proxy = '_z_proxy_'
    page_request = '_page_request_'

    def __init__(self):
        self.r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)

    def process_request(self, request, spider):
        pass
        # proxy_dic = self.r.hgetall('raw_proxy')
        # proxy_dic_keys = proxy_dic.keys()
        # 30s请求一次

        # 更新api
        page = None
        if 'page' in request.meta:
            page = request.meta['page']
        check_api = self.r.get(self.api_hold)
        if not check_api:
            proxy = requests.get(
                url='http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=2430071be5f941ffa7161d8fb3ca0327&count=10&expiryDate=0&format=1&newLine=2').json()
            self.r.set(self.api_hold, 1)
            self.r.expire(self.api_hold, 10)
            if 'msg' in proxy:
                for item in proxy['msg']:
                    proxy = item['ip'] + ':' + item['port']
                    check_finish = self.r.sismember(self.proxy_key_finish, proxy)
                    if not check_finish:
                        check_has = self.r.hget(self.z_proxy, proxy)
                        if not check_has:
                            self.r.hset(self.z_proxy, proxy, 1)


        #重复请求
        if page:
            request_proxy = self.r.hget(self.page_request, page)
            if request_proxy:
                self.r.sdd(self.proxy_key_finish, request_proxy)
                self.r.hdel(self.z_proxy, request_proxy)

        proxy_all = self.r.hgetall(self.z_proxy)
        if proxy_all.keys():
            proxy = random.choice(list(proxy_all.keys()))
            if proxy:
                times = proxy_all[proxy]
                if int(times) > 5000:
                    self.r.hdel(self.z_proxy, proxy)
                    self.r.sdd(self.proxy_key_finish, proxy)
                else:
                    self.r.hincrby(self.z_proxy, proxy, 1)

                self.r.hset(self.page_request, page, proxy)

                print('this is proxy ' + proxy)
                request.meta['proxy'] = "http://" + proxy
                request.meta['raw_proxy'] = proxy

    def process_response(self, request, response, spider):
        text = response.text
        print(response.status)
        if text == '警告!由于你恶意访问,您的IP已被记录!':
            if 'raw_proxy' in request.meta:
                proxy = request.meta['raw_proxy']
                # delete = "http://127.0.0.1:5010/delete/?proxy={}".format(proxy)
                # requests.get(url = delete)
                self.r.sdd(self.proxy_key_finish, proxy)
                self.r.hdel(self.z_proxy, proxy)
                print('this is request delete ip: ' + proxy)
            return request
        return response
