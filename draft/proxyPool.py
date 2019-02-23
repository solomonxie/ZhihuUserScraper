import random
import requests
import json

def get_proxies():
    url = 'http://127.0.0.1:8000?count=5'
    r = requests.get(url=url)
    return json.loads( r.text )


def parse_proxy(d):
    return {
        # 'http': 'http://{}:{}'.format(d[0],d[1]),
        'https': 'https://{}:{}'.format(d[0],d[1])
    }

def get_valid_proxy():
    ips = get_proxies()
    ip = random.choice(ips)
    proxy = {
        'https': 'https://{}:{}'.format(ip[0],ip[1])
    }
    addr = ip[0]
    try:
        # r = requests.get('https://httpbin.org/ip', proxies=proxy, timeout=5)
        # print( '[VALID-IP]', r.text )
        r = requests.get('https://baidu.com', proxies=proxy, timeout=3)
        print( '[VALID-IP]', ip )
        return proxy
    except Exception as e:
        print( '[INVALID-IP]', ip )
        r = requests.get(url='http://127.0.0.1:8000/delete?ip='+addr)
        print( r.text )
        get_valid_proxy()


if __name__ == '__main__':
    for i in range(20):
        get_valid_proxy()

