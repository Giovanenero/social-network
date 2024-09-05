from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['instagram']
collection_profiles = db['profiles']
collection_posts = db['posts']
collection_statistics = db['statistics']
collection_statistics.create_index('userid')

profiles = list(collection_profiles.find())

for profile in profiles:
    posts = list(collection_posts.find({'userid': profile['userid']}))
    likes = 0
    comments = 0

    for post in posts:
        likes += post.get('likeCount', 0)
        comments += post.get('commentCount', 0)

    followers = profile.get('followers', 0)

    data = {
        'userid': profile['userid'],
        'likes': likes,
        'comments': comments,
        'followers': followers,
        'date': datetime.today(),
    }

    primeiro_dia_mes_atual = datetime.today().replace(day=1)
    ultimo_dia_mes_passado = primeiro_dia_mes_atual - timedelta(days=1)
    primeiro_dia_mes_passado = ultimo_dia_mes_passado.replace(day=1)

    print(primeiro_dia_mes_atual)
    print(primeiro_dia_mes_passado)
    print(ultimo_dia_mes_passado)
    print('')

    query = {'date': data['date'], 'userid': data['userid']}

    if collection_statistics.count_documents(query) > 0:
        collection_statistics.update_one(query, {"$set": data})
    else:
        collection_statistics.insert_one(data)
