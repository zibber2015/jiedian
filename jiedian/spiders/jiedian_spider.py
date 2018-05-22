from scrapy.spiders import Spider, Request
from jiedian.items import JiedianItem
from scrapy.exceptions import CloseSpider
import time
from jiedian.helpers import helpers
import json


class JiedianSpider(Spider):
    name = 'jiedian'
    allowed_domains = [
        'jiedian.com',
        'dianping.com'
    ]

    def start_requests(self):
        # 城市
        poi_sql = "select page from `t_poi` order by page desc limit 1"
        ret = helpers.mysql(self, poi_sql)

        last_page = 1
        if ret:
            last_page = ret[0]['page']

        # for i in range(1, 28570000):
        for i in range(int(last_page) + 1, 28570000):
            url_city = 'http://www.poi86.com/poi/{0}.html'.format(str(i))
            yield Request(url = url_city, callback=self.parse_poi, meta={'page': i})


        #爬jiedian
        return
        url = 'https://api.ankerjiedian.com/index.php'
        body = {
            "header": {
                "type": "device",
                "service": "sharedCharging",
                "api": "YBusiness.getSimpleBusinessListByPosition",
                "source": "",
                "msg_id": "325263F4-4978-96AA-3CD7-5BC20B4B4C3F",
                "client_v": "1.971",
                "applet": "wxapp",
                "access_token": "eyJleHAiOjE1MjY5Mjc1NTMsImtpZCI6MX0.eyJ1aWQiOiJmYmY5ZTE2Ni1hNjZhLTRkYjYtYTc3Yy0xZWVlZGY5MmM3ZDMiLCJ1c2VyX2lkIjoiMTg1NTc5ODMifQ.gAHadDUxEwxeNnmjX85FtuTm3p9URvHc3AZiL1JlD7A"
            },
            "body": {
                "longitude": 113.94086359696294,
                "latitude": 22.538313734395654
            }
        }
        for i in range(1, 1000):
            yield Request(url=url, method='POST', callback=self.parse_dianping, body=json.dumps(body), dont_filter=True)

    def parse_poi(self, response):
        page = response.meta['page']
        name = response.xpath('/html/body/div[2]/div[1]/div[1]/h1/text()').extract_first(default='')
        province = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[1]/a/text()').extract_first(default='')
        city = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[2]/a/text').extract_first(default='')
        area = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[3]/a/text()').extract_first(default='')
        address = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[4]/text()').extract_first(default='')
        tel = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[5]/text()').extract_first(default='')
        category = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[6]/a/text()').extract_first(default='')
        tag_o = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[7]/a/text()').extract_first(default='')
        tag = ''
        if tag_o:
            tag = tag_o.strip('(')
        
        # 大地坐标
        earth = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[8]/text()').extract_first(default='')
        earth_long = 0
        earth_lat = 0
        if earth:
            earth_f = earth.strip(' ').split(',')
            earth_long = earth_f[0]
            earth_lat = earth_f[1]

        #火星坐标
        mars = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[9]/text()').extract_first(default='')
        mars_long = 0
        mars_lat = 0
        if mars:
            mars_f = mars.strip(' ').split(',')
            mars_long = mars_f[0]
            mars_lat = mars_f[1]     
         
        # 百度
        baidu = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li[10]/text()').extract_first(default='')
        baidu_long = 0
        baidu_lat = 0
        if baidu:
            baidu_f = baidu.strip(' ').split(',')
            baidu_long = baidu_f[0]
            baidu_lat = baidu_f[1]

        item = JiedianItem()
        now = int(time.time())
        sql = 'insert into t_poi (`province`, `city`, `area`, `address`, `tel`, `category`, `tag`, `earth_long`, `earth_lat`, `mars_long`, `mars_lat`, `baidu_long`, `baidu_lat`, `page`, `created_at`, `name`) ' \
              'values (\"{0}\",\"{1}\", \"{2}\", \"{3}\", \"{4}\", \"{5}\", \"{6}\", \"{7}\", \"{8}\", \"{9}\", \"{10}\", \"{11}\", \"{12}\", \"{13}\", \"{14}\", \"{15}\")'.format(
            province, city, area, address, tel, category, tag, earth_long, earth_lat, mars_long, mars_lat, baidu_long, baidu_lat, page, now, name
        )

        item['sql'] = sql
        yield item

    def parse_jiedian_city(self, response):
        if response.status == 200:
            keyword_path = '//*[@id="main"]/div[4]/ul/li[*]/div[1]/text()'
            keyword = response.xpath(keyword_path).extract()
            if not keyword:
                return

            name_path = '//*[@id="main"]/div[4]/ul/li[*]/div[2]/div/a/text()'
            city_name = response.xpath(name_path).extract()

            url_path = '//*[@id="main"]/div[4]/ul/li[*]/div[2]/div/a/@href'
            url = response.xpath(url_path).extract()

            url_f = list(map(lambda x: x[2:], url))

            short = []
            for i in url_f:
                pos = i.find('/')
                short.append(i[pos + 1:])
            
            
            item = JiedianItem()
            all_in = []
            for i in range(len(city_name)):
                sql = 'insert into t_city (`url`, `name`, `short`, `created_at`) values ("%s","%s","%s",%d)' % (
                    url_f[i], city_name[i], short[i], int(time.time()))
                item['sql'] = sql
                yield item
