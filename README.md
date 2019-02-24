# Test Case Study: Zhihu User Scraper

Test case study:
Scrap User infromations from Zhihu.com.


## Case Requirements

- Build a Web Scraper to scrape all user informations from Zhihu.com
- User information includes: Name, URL, etc.
- Store data in a proper way.



## Recursive Concurrency Paradox



FLOW:
```
0-Depth:
    ROOT -> tasks[0],next[] -> parse_profile(0) => {parse_paging(0)} => tasks[],next[1,2,3] ->
1-Depth:
    tasks,next=[],tasks -> tasks[1,2,3], next[] ->
    parse_profile([1,2,3]) => {parse_paging(tasks)} => tasks[], next[4,5,6,7,8,9,10,11,12]
```





## Case Strategy

Scraping Approaches:
- Official API(JSON) Retriving
- ~~HTML Parsing~~ (Not necessary!)

Scraping Frameworks:
- Scrapy
- None: Simple scripts

~~Scraping Flow:~~
1. Starts with one or multiple V-User
2. Retrive his profile Informations
3. Get all the urls of his `Subscriptions` & `Followers`
4. Read profile information of each user from the url-list
5. Repeat step-3



## Case Analysis

### HTML approach

Entry Points:
- User Profile: `https://www.zhihu.com/people/{username}`
- Followers: `https://www.zhihu.com/people/{username}/followers`
- Subscriptions: `https://www.zhihu.com/people/zhang-jia-wei/following`

Paging: `https://www.zhihu.com/people/zhang-jia-wei/following?page=2`



### API approach

Entry points:
- User Profile: `https://www.zhihu.com/api/v4/members/{username}`
- Followers: `https://www.zhihu.com/api/v4/members/{username}/followers`
- Subscriptions: `https://www.zhihu.com/api/v4/members/{username}/followees`


Paging:
- `limit`: 20 items/page
- `offset`: starts from 0

Options(`include`-> extra informations)
- Profile includes: `locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,included_answers_count,included_articles_count,included_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,is_org_createpin_white_user,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics`
- Follower includes: `answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics`
- Subscription includes: `answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics`





## Code Design



## Storage

Storage of URLs:
- The data takes 44.99604 byte/url, 43 MB/1M urls, 42 GB/1B urls
- Zhihu.com has 220 million users, So urls will take 9.2 GB.
- ZIP conpression rate: 0.29%, which reduces the whole pack to 27MB
- Database compression rate is similar or even further.

Storage of IDs:
- No need to store whole url but an unique ID
- each ID takes 4 byte, 840MB for 220 million IDs.
- After compression, it'll take much less space, say 4MB.


Storage of profile infos:


## Disclaimer

This project is ONLY for test case study.


