import random
import requests
import json

from threading import Thread

proxies = []

def get_ips(count=20):
    try:
        r = requests.get(url='http://127.0.0.1:8000?count={}'.format(count))
        return json.loads( r.text )
    except Exception as e:
        print('[ERR] Proxy Pool Server', e)


def get():
    global proxies
    if proxies:   # Directly return IP in the pool
        ip = proxies.pop(0)
        print( '[USING-IP]', ip )
        return ip
    else:  # Retrive when pool's empty
        # Directly yield out proxies without validation
        proxies = [parse_proxy(p) for p in get_ips(200)]
        # Validate each IP before return
        # filter_valid()
        # return get()

def filter_valid():
    print('[PROXY] FILTERING VALID IPs.')
    proxies = [parse_proxy(p) for p in get_ips(100)]
    threads = []
    for p in proxies:
        # del_invalid(proxies, i)
        threads.append( Thread(target=validate, args=(p,)) )
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # print('[VALID-IPs]', len(proxies))

def validate(proxy):
    global proxies
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}
    url = 'https://baidu.com'
    try:
        # print('[TRY]', n, proxies[n])
        r = requests.get(url=url, headers=headers, proxies=proxy, timeout=2)
        proxies.append(proxy)
    except Exception as e:
        # print(e)
        # print('[INVALID]', proxy)
        delete(proxy)
        pass


def parse_proxy(d):
    return {
        'https': 'https://{}:{}'.format(d[0],d[1]),
        'ip': d[0]
    }


def delete(proxy):
    try:
        r = requests.get(url='http://127.0.0.1:8000/delete?ip={}'.format(proxy['ip']))
    except Exception as e:
        print('[ERR] Proxy Pool Server', e)


if __name__ == '__main__':
    # for i in range(20):
        # get_valid_proxy()
    print('[PROXY]', get())
