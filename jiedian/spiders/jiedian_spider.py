from scrapy.spiders import Spider, Request
from jiedian.items import JiedianItem
from scrapy.exceptions import CloseSpider
import time


class JiedianSpider(Spider):
    name = 'jiedian'
    allowed_domains = [
        'jiedian.com',
        'dianping.com'
    ]

    def start_requests(self):
        headers = {
            # GET / shop / 96444268 HTTP / 1.1
            "Host": "www.dianping.com",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": 1,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
            "Cookie": "cy=7; cityid=7; cye=shenzhen; _lxsdk_cuid=15f5250cb30c8-05b4f6925684bc-31637c01-1fa400-15f5250cb30c8; _lxsdk=15f5250cb30c8-05b4f6925684bc-31637c01-1fa400-15f5250cb30c8; _hc.v=55d8ea44-5103-745f-acd8-dea3721a29ea.1508914548; s_ViewType=10; wed_user_path=2784|0; aburl=1; cityInfo=%7B%22cityId%22%3A7%2C%22cityEnName%22%3A%22shenzhen%22%2C%22cityName%22%3A%22%E6%B7%B1%E5%9C%B3%22%7D; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1520731879; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1520731879; __mta=44799643.1520667780709.1520731814744.1520732063322.6; lastVisitUrl=%2Fshenzhen%2Fhotel%2F; selectLevel=%7B%22level1%22%3A%221%22%7D; cy=24; cye=shijiazhuang; _lxsdk_s=16212adf89a-a32-59-65e%7C%7C696",
            "If-None-Match": "7cdbb85f0c0e6a0261ce50ce41fa56c9",
            "If-Modified-Since": "Fri, 09 Mar 2018 17:08:11 GMT"
        }
        # http: // www.dianping.com / robots.txt
        # for i in range(1000000, 10000000):
        #     url = 'http://www.dianping.com/shop/' + str(i)
        #     yield Request(url=url, meta={'current': i},
        #                   callback=self.parse_jiedian)

        yield Request(url = 'http://www.dianping.com/shop/96444268', callback=self.parse_jiedian, headers=headers)

    def parse_jiedian(self, response):
        if response.status == 200:
            location = response.xpath('//*[@id="logo-input"]/div[1]/a[2]/span[2]/text()').extract()
            if not location:
                return

            first_menu = response.xpath('//*[@id="body"]/div/div[1]/a[1]/text()').extract()
            first_menu_sub = first_menu[location:]
            # 分类
            category = response.xpath('//*[@id="body"]/div/div[1]/a[2]/text()').extract()
            #区
            district = response.xpath('//*[@id="body"]/div/div[1]/a[3]/text()').extract()
            #区域
            area = response.xpath('//*[@id="body"]/div/div[1]/a[4]/text()').extract()
            #商铺
            shop_name = response.xpath('//*[@id="body"]/div/div[1]/a[5]/text()').extract()
            #评分
            vote_star = response.xpath('//*[@id="basic-info"]/div[1]/span[1]/@title').extract()
            #评论数
            commit_num = response.xpath('//*[@id="reviewCount"]/text()').extract()
            commit_num_sub = commit_num[:-3]
            #口味
            taste = response.xpath('//*[@id="comment_score"]/span[1]/text()').extract()
            taste_sub = taste[:-3]
            #人均
            consume = response.xpath('//*[@id="avgPriceTitle"]/text()').extract()

            #环境
            env = response.xpath('//*[@id="comment_score"]/span[2]/text()').extract()
            env_sub = env[:-3]
            #服务
            server = response.xpath('//*[@id="comment_score"]/span[3]/text()').extract()
            server_sub = server[:-3]
            #地址
            address = response.xpath('//*[@id="basic-info"]/div[2]/span[2]/text()').extract()
            #tel
            tel = response.xpath('//*[@id="basic-info"]/p/span[2]/text()').extract()
            #营业时间
            business_time = response.xpath('//*[@id="basic-info"]/div[4]/p[1]/span[2]/text()').extract()

            #local
            local = response.xpath('//*[@id="map"]/img/@src').extract()
            #经度
            long = local[-20:-12]
            #维度
            lat = local[-10:]

            #存表
            item = JiedianItem()
            item['location'] = location
            item['menu'] = first_menu_sub
            item['category'] = category
            item['district'] = district
            item['area'] = area
            item['shop_name'] = shop_name
            item['vote_star'] = vote_star
            item['commit_num'] = commit_num_sub
            item['taste'] = taste_sub
            item['consume'] = consume
            item['env'] = env_sub
            item['server'] = server_sub
            item['address'] = address
            item['tel'] = tel
            item['business_time'] = business_time
            item['long'] = long
            item['lat'] = lat
            item['created_at'] = int(time.time())

            item['dbname'] = 'd_dazhong'
            yield item