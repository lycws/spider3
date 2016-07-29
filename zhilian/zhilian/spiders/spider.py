#coding:utf-8

import scrapy
import random
from ..settings import *
from scrapy.http import Request
from ..items import *

class Spider(scrapy.Spider):
    name = "spider"
    start_urls = []
    header = {
            #':method': 'GET',
            #':scheme': 'https',
            ':version': 'HTTP/1.1',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
        }
    comset = set()

    def parse(self, response):
        if response.meta['type'] == 1:
            itemlist = response.xpath("//table[@class='newlist']")

            for it in itemlist:
                company = it.xpath("tr/td[@class='gsmc']/a/text()").extract()
                url = it.xpath("tr/td[@class='zwmc']/div/a/@href").extract()
                if len(company) != 0:
                    company = company[0].encode('utf-8')
                    url = url[0].encode('utf-8')

                if len(company) != 0 and company not in self.comset:
                    self.comset.add(company)
                    yield Request(url, meta={'type': 2}, headers=self.header)

        elif response.meta['type'] == 2:
            comname = response.xpath("//div[@class='company-box']/p/a/text()").extract()[0].encode('utf-8')
            company = response.xpath("//div[@class='company-box']/ul/li")
            item = ComItem()
            for com in company:
                title = com.xpath("span/text()").extract()[0].encode('utf-8')
                if title == '公司地址：':
                    adr = com.xpath("strong/text()").extract()[0].encode('utf-8')
                    adr = adr.strip().lstrip().rstrip(',')
                    item['comname'] = comname
                    item['comadr'] = adr
                    yield item
                    break

    def start_requests(self):
        input = "阿里巴巴"
        url = "http://sou.zhaopin.com/jobs/searchresult.ashx?jl=选择地区&kw=" + input + "&p=1&kt=2"
        user_agent = random.choice(USER_AGENTS)
        self.header['User-Agent'] = user_agent
        yield Request(url, meta={'type': 1 }, headers=self.header)