from datetime import datetime
import instaloader
import requests
import os
from pymongo import MongoClient
import gridfs
from dotenv import load_dotenv

client = MongoClient('mongodb://localhost:27017/')
db = client['instagram']
collection = db['profiles']
fs = gridfs.GridFS(db)

L = instaloader.Instaloader()

load_dotenv("../.env")
EMAIL = os.getenv("INSTAGRAM_EMAIL")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

def get_profile(username, file_path):
    profile = instaloader.Profile.from_username(L.context, username)
    file = fs.find({'filename': {'$regex': f"{username}_profile_pic.*"}})[0]
    result = {}
    result['username'] = profile.username
    result['fullname'] = profile.full_name
    result['biography'] = profile.biography
    result['externalUrl'] = profile.external_url
    result['followers'] = profile.followers
    result['followees'] = profile.followees
    result['mediacount'] = profile.mediacount
    result['userid'] = profile.userid
    result['url'] = f"http://localhost:5000/instagram/image/{file._id}" if file else ""
    result['extraction'] = str(datetime.now())

    try:
        response = requests.get(profile.profile_pic_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
                print(f'Imagem de perfil salva em: {file_path}')
    except:
        print(f"Não foi possível fazer download da imagem do {username}")

    return result

def upload_image(username, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            file_data = f.read()
            file_id = fs.put(file_data, filename=f'{username}_profile_pic.jpg')
            if os.path.exists(file_path):
                os.remove(file_path)
            print(f"id do arquivo: {file_id}")
            return file_id
    else:
        print(f"path {file_path} não existe!")
        return ''

usernames = ['wise.bifor', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.cado', 'wise.systems']

L.login(EMAIL, PASSWORD)

for username in usernames:
    file_path = os.path.join('downloads', f'{username}_profile_pic.jpg')
    try:
        data = get_profile(username, file_path)
        query = {'username': username}
        if len(list(collection.find(query))) > 0:
            update_data = {"$set": data}
            collection.update_one(query, update_data)
            print("imagem atualizada no mongodb")
        else:
            collection.insert_one(data)
            print("imagem inserida no mongodb")
    except:
        if os.path.exists(file_path):
            os.remove(file_path)

# similar_accounts = profile.get_similar_accounts()
# for similar_profile in similar_accounts:
#     print(f"Conta semelhante: {similar_profile.username}")

# for post in profile.get_tagged_posts():
#     print(f"Postagem {post.shortcode}: {post.caption}")



