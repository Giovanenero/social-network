from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['instagram']
collection_profiles = db['profiles']
collection_posts = db['posts']
collection_statistics = db['statistics']

profiles = list(collection_profiles.find())

date_today = str(datetime.today().date())

for profile in profiles:
    userid = profile['userid']
    posts = list(collection_posts.find({'userid': userid}))
    likes = 0
    comments = 0

    for post in posts:
        likes += post.get('likeCount', 0)
        comments += post.get('commentCount', 0)

    followers = profile.get('followers', 0)

    data = {
        'userid': userid,
        'likes': likes,
        'comments': comments,
        'followers': followers,
        'date': date_today,
    }

    query = {'date': date_today, 'userid': userid}
    statistics = list(collection_statistics.find({'userid': userid}))
    collection_statistics.update_one(query, {"$set": data}, upsert=True)

        
date_30_days_ago = datetime.fromisoformat(date_today) - timedelta(days=30)
date_30_days_ago = date_30_days_ago.date()
statistics = list(collection_statistics.find())
for statistic in statistics:
    if date_30_days_ago > datetime.fromisoformat(statistic['date']).date():
        collection_statistics.delete_one({'date': statistic['date']}) 
