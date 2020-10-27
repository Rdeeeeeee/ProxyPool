from multiprocessing import Process
from api import app
from getter import Getter
from tester import Tester
import time

TEST_CYCLE = 20
GETTER_CYCLE = 60
TEST_ENABLED = True
GETTER_ENABLED = False
API_ENABLED = True
API_HOST = '127.0.0.1'
API_PORT = 5555
API_THREADED = True


class Scheduler():
    def schedule_tester(self, cycle=TEST_CYCLE):
        """定时检测代理"""
        tester = Tester()
        while True:
            print('测试器开始运行')
            tester.run()
            print('schedule_tester 休息1min')
            time.sleep(cycle)

    def schedule_get(self, cycle=GETTER_CYCLE):
        """定时获取代理"""
        getter = Getter()
        while True:
            print('开始抓取代理')
            getter.run()
            print('schedule_get 休息1min')
            time.sleep(cycle)

    def schedule_api(self):
        """开启api"""
        app.run(host=API_HOST, port=API_PORT, threaded=API_THREADED)

    def run(self):
        print('代理池开始运行')
        if TEST_ENABLED:
            test_process = Process(target=self.schedule_tester)
            test_process.start()

        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_get)
            getter_process.start()

        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()

        test_process.join()
        api_process.join()


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.run()
