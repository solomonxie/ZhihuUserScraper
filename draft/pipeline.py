from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017')
db = client.test
c1 = db.c1
# c1.insert({'name':'jason', 'age':11})
result = c1.find({'name':'peter'})

for item in result:
    print(item, item.get('xxx'))

