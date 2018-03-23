# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import pymysql.cursors
from jiedian import settings

class JiedianPipeline(object):
    def process_item(self, item, spider):
        connection = pymysql.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            db=settings.MYSQL_DBNAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                now = int(time.time())
                table = item['table']
                if item:
                    sql = "insert into " + table +" (`title`, `page`, `img`, `text`, `content`, `create_time`) values (%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (str(item['title']), item['page'], str(
                        item['img']), str(item['text']), str(item['content']), now))
                    connection.commit()
                    print(item['page'], '已经储存')
        finally:
            connection.close()
