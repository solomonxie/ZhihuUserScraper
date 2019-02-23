import random
import requests
import json

from threading import Thread

proxies = []
invalid = []

def get_ips(count=20):
    url = 'http://127.0.0.1:8000?count={}'.format(count)
    try:
        r = requests.get(url=url)
        return json.loads( r.text )
    except Exception as e:
        print('[ERR]', e)


def validate(proxy):
    global proxies
    try:
        # print('[TRY]', n, proxies[n])
        r = requests.get('https://baidu.com', proxies=proxy, timeout=3)
        proxies.append(proxy)
    except Exception as e:
        # print(e)
        # print('[INVALID]', proxy)
        r = requests.get(url='http://127.0.0.1:8000/delete?ip={}'.format(proxy['ip']))
        pass


def filter_valid():
    proxies = [parse_proxy(p) for p in get_ips(10)]
    threads = []
    for p in proxies:
        # del_invalid(proxies, i)
        threads.append( Thread(target=validate, args=(p,)) )
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def parse_proxy(d):
    return {
        'https': 'https://{}:{}'.format(d[0],d[1]),
        'ip': d[0]
    }

def get_proxy():
    filter_valid()
    global proxies
    # print('[VALID-IPs]', len(proxies))
    ip = random.choice(proxies)
    print( '[SWITCH-IP]', ip )
    return ip


if __name__ == '__main__':
    # for i in range(20):
        # get_valid_proxy()
    print('[PROXY]', get_proxy())
