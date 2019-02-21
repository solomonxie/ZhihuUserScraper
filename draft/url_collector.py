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

# Initiate entry points
ids = {'sizhuren'}


# Load login info
with open('/tmp/headers.json', 'r') as f:
    headers = json.loads(f.read())

# Get his subscriptions
def get_subscriptions(uid=None, degree=0):
    url = 'https://www.zhihu.com/api/v4/members/{}/followees'.format(uid)
    # url = 'https://www.zhihu.com/api/v4/members/{}/followers'.format(uid)
    total = 20
    # Paging
    offset = 0
    while offset <= total:
        try:
            params = {'limit':20, 'offset':offset, 'include':'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'}
            headers['referer'] = '{}?page={}'.format(url, round(offset/20+1))
            r = requests.get(url, params=params, headers=headers, timeout=10)
            time.sleep(1+random.random()*100%3)
            if r.status_code != 200:
                print('[RESP]', r.status_code)
                continue
        except Exception as e:
            print( '[ERR:requests]', e, '\n', url, params, headers)
            break
        try:
            info = r.json()
        except Exception as e:
            print( '[ERR:r.json()]', r.status_code, e )
            break

        total = info.get('paging',{}).get('totals', 0)
        print('{} [{}D] {}/{} {}'.format('\t'*degree, degree, offset, total, url))

        # Get 20 sub-ids form this page
        for item in info.get('data', []):
            token = item.get('url_token')
            print( '\t'*(degree+1), token )
            # Recursively load the sub-ids of this sub-id
            if token not in ids and degree < 7:
                get_subscriptions(token, degree+1)
            # Save the retrived ID when it's "fully" retireved
            ids.add(token)

        # Ready for next page
        offset += 20


# --------------------[ ENTRANCE ]---------------------------------l
if __name__ == '__main__':
    for uid in ids:
        get_subscriptions(uid)
