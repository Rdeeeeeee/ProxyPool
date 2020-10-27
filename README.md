# README

> 参考自崔大大的《Python3 网络爬虫开发实战》
>
> Github地址：https://github.com/Python3WebSpider/ProxyPool

2020.10.27

`getter.py`：获取代理模块

`tester.py`：检测代理模块，筛选可用代理

`db.py`：数据库模块，使用`Redis`数据库

`api.py`：接口模块，方便可用获取代理

`scheduler.py`：调度模块，调度启动`getter`、`tester`、`api`模块

`utils.py`：函数模块

下一步：将代理库与爬虫程序相连，使爬虫程序可以更换代理爬虫