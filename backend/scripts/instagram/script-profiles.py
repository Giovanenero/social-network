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
collection.create_index('userid', unique=True)
fs = gridfs.GridFS(db)

# Carregar variáveis de ambiente
load_dotenv("../../../.env")
EMAIL = os.getenv("INSTAGRAM_EMAIL")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

L = instaloader.Instaloader()
L.login(EMAIL, PASSWORD)

def get_profile(profile):
    result = {}
    result['username'] = profile.username
    result['fullname'] = profile.full_name
    result['biography'] = profile.biography
    result['externalUrl'] = profile.external_url
    result['followers'] = profile.followers
    result['followees'] = profile.followees
    result['mediacount'] = profile.mediacount
    result['userid'] = str(profile.userid)

    return result

usernames = ['wise.bifor', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.cado', 'wise.systems']

def upload_imagem(username, profile):
    try: 
        file_path = os.path.join('../downloads', f'{username}_profile_pic.jpg')
        response = requests.get(profile.profile_pic_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
                print(f'Imagem de perfil salva em: {file_path}')

            existing_file = db.fs.files.find_one({'filename': f'{username}_profile_pic.jpg'})
            if existing_file:
                existing_file_id = existing_file['_id']
                fs.delete(existing_file_id)
                print(f'Imagem de perfil existente {existing_file_id} removida do MongoDB')

            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_id = fs.put(file_data, filename=f'{username}_profile_pic.jpg')
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f"Imagem de perfil {file_id} foi importado ao mongodb")

            if os.path.exists(file_path):
                os.remove(file_path)

            return f"http://localhost:5000/instagram/image/{file_id}" 
    except:
        print(f'não foi possível importar imagem de {username} para o mongodb')

    return ''

for username in usernames:
    profile = instaloader.Profile.from_username(L.context, username)
    try:
        data = get_profile(profile)
        data['url'] = upload_imagem(username, profile)
        data['extraction'] = str(datetime.now())
        query = {'username': username}
        if len(list(collection.find(query))) > 0:
            update_data = {"$set": data}
            collection.update_one(query, update_data)
            print("imagem atualizada no mongodb")
        else:
            collection.insert_one(data)
            print("imagem inserida no mongodb")
        print('')
    except: 
        print(f"não foi possível extrair dados de {username}")

# similar_accounts = profile.get_similar_accounts()
# for similar_profile in similar_accounts:
#     print(f"Conta semelhante: {similar_profile.username}")

# for post in profile.get_tagged_posts():
#     print(f"Postagem {post.shortcode}: {post.caption}")




