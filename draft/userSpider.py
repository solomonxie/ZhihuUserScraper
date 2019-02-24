import requests
import time
import random
import json
from threading import Thread

import proxyPool

from pymongo import MongoClient
DB_USERS = MongoClient('mongodb://127.0.0.1:27017').zhihu.users


URL_PROFILE = 'https://www.zhihu.com/api/v4/members/{username}?include=locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,included_answers_count,included_articles_count,included_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,is_org_createpin_white_user,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
URL_FOLLOWEE = 'https://www.zhihu.com/api/v4/members/{username}/followees?limit=20&offset={offset}&include=answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
URL_FOLLOWER = 'https://www.zhihu.com/api/v4/members/{username}/followers?limit=20&offset={offset}&include=answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
HEADERS = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}

class UserSpider(object):

    # Initiate entry points
    START_USERS = {'sizhuren'}
    PROXY = proxyPool.get()
    TASKS = ['sizhuren']  #(Linear+=Concurrent) For paging requests
    DEEPER_TASKS = []  #(Recursive) Tasks to do 1-level deeper

    def __init__(self):
        for username in self.START_USERS:
            self.parse_profile(username)


    def parse_profile(self, username):
        data = self.Request(URL_PROFILE.format(username=username))
        data['_id'] = username
        DB_USERS.update_one({'_id':username}, {"$set":data}, upsert=True)
        print('[OK] User:', data['name'])

        # [Linear] Retrive CURRENT User's all direct related users
        for url in self.gen_urls(username, data['follower_count'], data['following_count']):
            self.TASKS.append(url)
            # Handle tasks if accumulated to a number
            if len(self.TASKS) >= 10:
                self.handle_tasks()
                break

        # [Recursive] 1-level deeper
        # HAS TO RUN AFTER ALL PAGES LOADED (TASK_USERS IS FILLED UP)
        # TO AVOID TO RECURSIVELY PILE UP THREADINGS
        # IT HAS TO BE 1 THREAD ONLY
        # ...


    # User-list pages all have same structure
    def parse_paging(self, response):
        # init list
        # requst..
        print('[OK] User List', response)



    # Round-robin multi-threading handling tasks(requests)
    def handle_tasks(self):
        # threads = [ Thread(target=self.Request, args=(url,self.parse_user_list,)) for url in self.TASKS ]
        threads = []
        while self.TASKS:
            url = self.TASKS.pop(0)
            threads.append(
                Thread(target=self.Request, args=(url,self.parse_paging,))
            )
        s = [t.start() for t in threads]
        j = [t.join() for t in threads]
        self.TASKS = [] # Clear task-queue

    def gen_urls(self, username, follower_count, followee_count):
        # Generate all user-lists (both followers & followees)
        for offset in range(0,follower_count,20):
            yield URL_FOLLOWER.format(username=username, offset=offset)
        for offset in range(0,followee_count,20):
            yield URL_FOLLOWEE.format(username=username, offset=offset)

    def Request(self, url, callback=None):
        # print('[REQ]', url)
        try:
            # response = requests.get(url, headers=HEADERS, proxies=self.PROXY, timeout=2)
            response = requests.get(url, headers=HEADERS, timeout=2)
            if response.status_code != 200:
                print('[RESP]', response.status_code)
                # proxyPool.delete(self.PROXY)
                self.PROXY = proxyPool.get()
                self.Request(url)
        except Exception as e:
            print( '[ERR:requests]', type(e).__name__)
            self.PROXY = proxyPool.get()
            self.Request(url)
        try:
            if callback:
                callback(response)
            else:
                return response.json()
        except Exception as e:
            print( '[ERR] Site reponse with invalid JSON\n', response.text )
            self.PROXY = proxyPool.get()
            self.Request(url)



# --------------------[ ENTRANCE ]---------------------------------l
if __name__ == '__main__':
    UserSpider()

