# Test Case Study: Zhihu User Scraper

Test case study:
Scrap User infromations from Zhihu.com.


## Case Requirements

- Build a Web Scraper to scrape all user informations from Zhihu.com
- User information includes: Name, URL, etc.
- Store data in a proper way.



## Case Strategy

Scraping Flow:
1. Starts with one or multiple V-User
2. Retrive his profile Informations
3. Get all the urls of his `Subscriptions` & `Followers`
4. Read profile information of each user from the url-list
5. Repeat step-3


Scraping Approaches:
- Official API(JSON) Retriving
- HTML Parsing (Not necessary!)

Scraping Frameworks:
- Scrapy
- None


## Case Analysis

### HTML approach

Entry point (User Profile):
`https://www.zhihu.com/people/{username}`

Followers:
`https://www.zhihu.com/people/{username}/followers`

Subscriptions:
`https://www.zhihu.com/people/zhang-jia-wei/following`

Paging:
`https://www.zhihu.com/people/zhang-jia-wei/following?page=2`



### API approach

Entry point (User Profile):
`https://www.zhihu.com/api/v4/members/{username}`

Followers:
`https://www.zhihu.com/api/v4/members/{username}/followers`

Subscriptions:
`https://www.zhihu.com/api/v4/members/{username}/followees`


Paging & Options:
- `limit`: 20 items/page
- `offset`: starts from 0
- `include`: extra informations


## Disclaimer

This project is ONLY for test case study.


