import requests


def get_page(url):
    """获取页面"""
    return requests.get(url).text