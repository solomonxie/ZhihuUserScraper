import random
import requests
import json

def get_proxies():
    url = 'http://127.0.0.1:8000?count=20'
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
    proxy = parse_proxy( ip )
    addr = ip[0]
    try:
        r = requests.get('https://httpbin.org/ip', proxies=proxy, timeout=5)
        print( '[VALID-IP]', r.text )
        return proxy
    except Exception as e:
        # r = requests.get(url='http://127.0.0.1:8000/delete?ip='+addr)
        # print( r.text )
        print( '\t[INVALID-IP]', ip )
        get_valid_proxy()


if __name__ == '__main__':
    for i in range(20):
        get_valid_proxy()

