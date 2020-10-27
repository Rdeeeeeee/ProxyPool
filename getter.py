import json
from utils import get_page
from pyquery import PyQuery as pq
from db import RedisClient

POOL_UPPER_THRESHOLD = 1000


class ProxyMetaClass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            print("name=%s and value=%s" % (k, v))  # 打印所有类属性出来
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=ProxyMetaClass):
    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            print("成功获取到代理", proxy)
            proxies.append(proxy)
        return proxies

    def crawl_xundaili(self):
        """获取讯代理"""
        start_url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=62016bab6a244cfa982c5c06d6cfdc65&orderno=YZ202010259301aCP6Bq&returnType=2&count=3'
        print('Crawling讯代理', start_url)
        html = get_page(start_url)
        if html:
            result = json.loads(html)
            proxies = result.get("RESULT")
            for proxy in proxies:
                yield proxy.get('ip') + ':' + proxy.get('port')

    def crawl_daili66(self, page_count=10):
        """获取66代理
        :param page_count: 页码
        :return 代理"""
        start_url = 'http://www.66ip.cn/{}.html'
        urls = [start_url.format(page) for page in range(1, page_count+1)]
        for url in urls:
            print('Crawling', url)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])
'''
    def crawl_proxy360(self):
        """获取proxy360
        :return 代理"""
        start_url = 'http://www.proxy360.cn/region/china'
        print('Crawling', start_url)
        html = get_page(start_url)
        if html:
            doc = pq(html)
            lines = doc('div[name="list_proxy_ip"]').items()
            for line in lines:
                ip = line.find('.tbBottomLine:nth-child(1)').text()
                port = line.find('.tbBottomLine:nth-child(2)').text()
                yield ':'.join([ip, port])

    def crawl_gouobanjia(self):
        """获取GouBanjia
        :return 代理"""
        start_url = 'http://www.goubanjia.com/free/gngn/index.shtml'
        print('Crawling', start_url)
        html = get_page(start_url)
        if html:
            doc = pq(html)
            tds = doc('td.ip').items()
            for td in tds:
                td.find('p').remove()
                yield td.text().replace(" ", "")
'''


class Getter(object):
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        """判断是否达到了代理池限制"""
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        print('获取器开始执行')
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
                for proxy in proxies:
                    self.redis.add(proxy)


if __name__ == '__main__':
    g = Getter()
    g.run()

