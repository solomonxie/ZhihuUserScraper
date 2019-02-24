"""
URL Collector
    It's only to collect URLs of user profile without retriving actual user data,
    to keep things simple & effective.

    Strategy:
    - Get his followers
        - `/{username}/followers?include=xxxxxx&limit=20&offset=0`
    - Get his subscriptions
        - `/{username}/followees?include=xxxxxx&limit=20&offset=0`

    Paging:
    - start with '?limit=20&offset=0'
    - Initially, `total=20`, `limit=20`, `offset=0`
    - `total` updated in each run
    - `offset+=20 if offset <= total`
"""

import requests
import time
import random
import json

import proxyPool

from pymongo import MongoClient
db_users = MongoClient('mongodb://127.0.0.1:27017').zhihu.users


# Initiate entry points
ids = {'sizhuren'}

proxy = proxyPool.get()

# Load login info
with open('/tmp/headers.json', 'r') as f:
    headers = json.loads(f.read())

# Get his subscriptions
def get_subscriptions(uid=None, degree=0):
    global proxy
    url = 'https://www.zhihu.com/api/v4/members/{}/followees'.format(uid)
    # url = 'https://www.zhihu.com/api/v4/members/{}/followers'.format(uid)
    total = 20
    offset = 0

    # Paging Loop
    while offset <= total:
        try:
            params = {'limit':20, 'offset':offset, 'include':'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'}
            headers['referer'] = '{}?page={}'.format(url, round(offset/20+1))
            r = requests.get(url, params=params, headers=headers, proxies=proxy, timeout=2)
            if r.status_code != 200:
                print('[RESP]', r.status_code)
                # proxyPool.delete(proxy)
                proxy = proxyPool.get()
                continue
        except Exception as e:
            print( '[ERR:requests]', type(e).__name__, '\n', url)
            proxy = proxyPool.get()
            continue
        try:
            info = r.json()
        except Exception as e:
            print( '[ERR] Site reponse with invalid JSON' )
            continue

        # Only pause when the proxy works
        # time.sleep( random.random()*100%2 )

        etag = r.headers.get('etag')
        total = info.get('paging',{}).get('totals', 0)
        users = info.get('data', [])  # Get 20 sub-ids form this page
        print('[{}D] {}/{} {}'.format(degree, offset, total, url))
        # print('{} [{}D] {}/{} {}'.format('\t'*degree, degree, offset, total, url))

        # In-page Loop
        for item in users:
            token = item.get('url_token')
            exists = db_users.find_one({'_id':token})
            # print( '[RECORD]', exists )
            if not exists:
                # Insert data to DB
                db_users.insert_one({'_id':token, 'followee_etag':etag})
                print( '\t'*(degree+1)+'[INSERT]', token )

        # In-page Loop
        for item in users:
            if degree<7 :
                # Dive-in Loop (Recursive) Load the sub-ids of this sub-id
                get_subscriptions(uid=item.get('url_token'), degree=degree+1)

        # Ready for next page
        offset += 20


# --------------------[ ENTRANCE ]---------------------------------l
if __name__ == '__main__':
    for uid in ids:
        get_subscriptions(uid)
