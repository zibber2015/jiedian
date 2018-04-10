from scrapy.spiders import Spider, Request
from jiedian.items import JiedianItem
from scrapy.exceptions import CloseSpider
import time
from jiedian.helpers import helpers


class JiedianSpider(Spider):
    name = 'jiedian'
    allowed_domains = [
        'jiedian.com',
        'dianping.com'
    ]

    def start_requests(self):
        # 城市
        city_sql = "select * from `t_city`"
        ret = helpers.mysql(self, city_sql)
        if not ret :
            url_city = 'http://www.dianping.com/citylist'
            yield Request(url = url_city, callback=self.parse_jiedian_city)



    def parse_jiedian(self, response):
        print(response.body)
        return
        if response.status == 200:
            # item['page'] = meta['current']
            location = response.xpath('//*[@id="logo-input"]/div[1]/a[2]/span[2]/text()').extract_first()
            if not location:
                return

            first_menu = response.xpath('//*[@id="body"]/div/div[1]/a[1]/text()').extract_frist()
            first_menu_sub = first_menu[(len(location) + 1):]

            # 分类
            category = response.xpath('//*[@id="body"]/div/div[1]/a[2]/text()').extract()
            #区
            district = response.xpath('//*[@id="body"]/div/div[1]/a[3]/text()').extract()
            #区域
            area = response.xpath('//*[@id="body"]/div/div[1]/a[4]/text()').extract()
            #商铺
            shop_name = response.xpath('//*[@id="body"]/div/div[1]/span/text()').extract()
            #评分
            vote_star = response.xpath('//*[@id="basic-info"]/div[1]/span[1]/@title').extract_first()
            vote_star_sub = vote_star[0]

            #评论数
            comment_num = response.xpath('//*[@id="reviewCount"]/text()').extract_first()
            comment_num_sub = comment_num[:-3]

            #人均
            consume = response.xpath('//*[@id="avgPriceTitle"]/text()').extract_first()
            comsume_sub = consume[3:-1]

            # 口味
            taste = response.xpath('//*[@id="comment_score"]/span[1]/text()').extract_first()
            taste_sub = taste[3:]

            #环境
            env = response.xpath('//*[@id="comment_score"]/span[2]/text()').extract_first()
            env_sub = env[3:]
            #服务
            server = response.xpath('//*[@id="comment_score"]/span[3]/text()').extract_first()
            server_sub = server[3:]
            #地址
            address = response.xpath('//*[@id="basic-info"]/div[2]/span[2]/text()').extract()
            #tel
            tel = response.xpath('//*[@id="basic-info"]/p/span[2]/text()').extract()
            #营业时间
            business_time = response.xpath('//*[@id="basic-info"]/div[4]/p[1]/span[2]/text()').extract()

            #local
            # local = response.xpath('//*[@id="staticPage"]/script[1]/text()').extract_first()
            # print(local)



            #存表
            item = JiedianItem()
            item['location'] = location
            item['menu'] = first_menu_sub
            item['category'] = category
            item['district'] = district
            item['area'] = area
            item['shop_name'] = shop_name
            item['vote_star'] = vote_star_sub
            item['comment_num'] = comment_num_sub
            item['taste'] = taste_sub
            item['consume'] = comsume_sub
            item['env'] = env_sub
            item['server'] = server_sub
            item['address'] = address
            item['tel'] = tel
            item['business_time'] = business_time
            # item['long'] = long
            # item['lat'] = lat
            item['table'] = 't_dazhong'
            print(item)
            return item

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
                sql = 'insert into t_city (`url`, `name`, `short`, `created_at`) values ("%s","%s","%s",%d)' % (url_f[i], city_name[i], short[i], int(time.time()))
                item['sql'] = sql
                yield item
