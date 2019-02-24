import requests
import time
import random
import json
from threading import Thread

import proxyPool

from pymongo import MongoClient
DB_USERS = MongoClient('mongodb://127.0.0.1:27017').zhihu.users


URL_PROFILE = 'https://www.zhihu.com/api/v4/members/{username}?include=locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,included_answers_count,included_articles_count,included_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,is_org_createpin_white_user,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
URL_FOLLOWEE = 'https://www.zhihu.com/api/v4/members/{username}/followees?offset={offset}&limit=20&include=answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
URL_FOLLOWER = 'https://www.zhihu.com/api/v4/members/{username}/followers?offset={offset}&limit=20&include=answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
HEADERS = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}

class UserSpider(object):

    # PROXY = proxyPool.get()
    PROXY = None

    DEPTH = 0

    # TASK QUEUES
    TASKS = ['SatNight']  #(Linear+=Concurrent) For paging requests
    DEEPER_TASKS = []  #(Recursive) Tasks to do 1-level deeper
    PAGING_TASKS = []  # [ (ID,Follower_count,Followee_count), (ID,Follower_count,Followee_count) ]

    def __init__(self):
        self.single_core()

    def single_core(self):
        # READ "PROFILES" & PREPARE FOR "PAGINGS"
        print('[START] PROFILES...')
        while self.TASKS:
            username = self.TASKS.pop(0)  #REMOVE FROM TASK QUEUE
            # RETRIVE PROFILE ACCORDING TO HIS ID
            profile = self.Request(URL_PROFILE.format(username=username))
            print('[OK] PROFILES', profile['name'])
            # INSERT PROFILE TO DB
            DB_USERS.update_one({'_id':username}, {"$set":profile}, upsert=True)
            c1,c2 = profile['follower_count'], profile['following_count']
            # GENERATE PAGING URL TASKS (NOT WHOLE URLs YET)
            self.PAGING_TASKS.append( (username,c1,c2) )

        # [PARALLEL] COLLECT IDs FROM USER LIST PAGES
        print('[START] PAGINGS...')
        while self.PAGING_TASKS:
            paging = self.PAGING_TASKS.pop(0)   #REMOVE FROM TASK QUEUE
            for url in self.gen_paginations( *paging ):
                jsondata = self.Request(url)
                user_list = jsondata.get('data')
                print('[PAGING]', len(user_list), len(self.DEEPER_TASKS), paging, url)
                # APPEND TO DEEPER TASK LIST FOR NEXT RUN
                self.DEEPER_TASKS += [ u['url_token'] for u in user_list ]
            print('[OK] PAGINGS', paging)

        # [RECURSIVE] READY FOR DEEPER LEVEL
        if self.DEEPER_TASKS:
            # PROMOTE SUB-TASKS TO CURRENT-TASKS
            self.TASKS, self.DEEPER_TASKS = self.DEEPER_TASKS, []
            # DIVE IN TO DEEPER DEPTH
            self.DEPTH+=1
            print('[D-{}] TASKS:{} DEEPER:{}'.format(self.DEPTH,len(self.TASKS), len(self.DEEPER_TASKS)))
            self.single_core()


    def multi_core(self):
        threads = []
        # READ "PROFILES" & PREPARE FOR "PAGINGS"
        while self.TASKS:
            username = self.TASKS.pop(0)  #REMOVE FROM TASK QUEUE
            threads.append( Thread(target=self.handle_profile, args=(username,)) )
        # RUN THREADS (START) & WAIT UNTIL FINISHED (JOIN)
        s = [t.start() for t in threads]
        j = [t.join() for t in threads]
        threads = []  #CLEAR THREADS POOL

        # [PARALLEL] COLLECT IDs FROM USER LIST PAGES
        while self.PAGING_TASKS:
            paging_args = self.PAGING_TASKS.pop(0)   #REMOVE FROM TASK QUEUE
            threads.append( Thread(target=self.handle_paging, args=(paging_args,)) )
        # RUN THREADS (START) & WAIT UNTIL FINISHED (JOIN)
        s = [t.start() for t in threads]
        j = [t.join() for t in threads]
        threads = []  #CLEAR THREADS POOL

        # [RECURSIVE] READY FOR DEEPER LEVEL
        if self.DEEPER_TASKS:
            self.multi_core()


    def handle_profile(self, username):
        username = self.TASKS.pop(0)  #REMOVE FROM TASK QUEUE
        # RETRIVE PROFILE ACCORDING TO HIS ID
        profile = self.Request(URL_PROFILE.format(username=username))
        # INSERT PROFILE TO DB
        DB_USERS.update_one({'_id':username}, {"$set":profile}, upsert=True)
        c1,c2 = profile['follower_count'], profile['following_count']
        # GENERATE PAGING URL TASKS (NOT WHOLE URLs YET)
        self.PAGING_TASKS.append( (username,c1,c2) )


    def handle_paging(self, paging):
        paging_args = self.PAGING_TASKS.pop(0)   #REMOVE FROM TASK QUEUE
        for url in self.gen_paginations( *paging_args ):
            jsondata = self.Request(url)
            user_list = jsondata.get('data')
            # APPEND IDs TO DEEPER TASK LIST FOR NEXT RUN
            self.DEEPER_TASKS += [ u['url_token'] for u in user_list ]


    def gen_paginations(self, username, follower_count, followee_count):
        # Generate all user-lists (both followers & followees)
        for offset in range(0,followee_count,20):
            yield URL_FOLLOWEE.format(username=username, offset=offset)
        for offset in range(0,follower_count,20):
            yield URL_FOLLOWER.format(username=username, offset=offset)

    def Request(self, url, callback={}):
        print('\t[REQ]', url, '\n')
        try:
            # response = requests.get(url, headers=HEADERS, proxies=self.PROXY, timeout=2)
            response = requests.get(url, headers=HEADERS, timeout=2)
            time.sleep( random.random()*100%4 )
            if response.status_code != 200:
                print('[ERR:response]', response.status_code)
                # proxyPool.delete(self.PROXY)
                # self.PROXY = proxyPool.get()
                self.Request(url, callback)
            try:
                if callback:  # REFERENCE VARIABLE, FOR RETURN VALUE IN THREAD
                    callback({'profile':response.json()})
                else:
                    return response.json()
            except Exception as e:
                print( '[ERR] Site reponse with invalid JSON\n', response.text )
                # self.PROXY = proxyPool.get()
                self.Request(url, callback)
        except Exception as e:
            print( '[ERR:requests]', type(e).__name__)
            # self.PROXY = proxyPool.get()
            self.Request(url, callback)



# --------------------[ ENTRANCE ]---------------------------------l
if __name__ == '__main__':
    UserSpider()

