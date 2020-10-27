import aiohttp
import asyncio
from db import RedisClient
import time
from aiohttp import ClientProxyConnectionError, ClientConnectorError, ServerDisconnectedError, ClientOSError, ClientHttpProxyError, ClientResponseError
from asyncio import TimeoutError


VALID_STATUS_CODE = [200]
TEST_URL = 'http://httpbin.org/get'
BATCH_TEST_SIZE = 100


class Tester(object):
    def __init__(self):
        self.redis = RedisClient()

    async def test_single_proxy(self, proxy):
        """测试单个代理
        :param proxy: 单个代理
        :return None"""
        conn = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试', proxy)
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15) as response:
                    if response.status in VALID_STATUS_CODE:
                        self.redis.max(proxy)
                        print('代理可用', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('代理请求失败', proxy)
            except (ClientConnectorError, ClientProxyConnectionError, ClientOSError, TimeoutError, ServerDisconnectedError, ClientHttpProxyError, ClientResponseError, AttributeError):
                self.redis.decrease(proxy)
                print('代理请求失败', proxy)

    def run(self):
        """测试主函数
        :return None"""
        print('测试器开始运行')
        try:
            proxies = self.redis.all()
            loop = asyncio.get_event_loop()
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i: i+BATCH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误', e.args)


if __name__ == '__main__':
    t = Tester()
    t.run()
