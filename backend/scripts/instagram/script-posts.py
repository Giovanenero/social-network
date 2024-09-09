from datetime import datetime
import time
import random
import instaloader
import requests
import os
from pymongo import MongoClient
import gridfs
from dotenv import load_dotenv

client = MongoClient('mongodb://localhost:27017/')
db = client['instagram']
collection_profiles = db['profiles']
collection_posts = db['posts']
collection_posts.create_index(['mediaid', 'userid'])
fs = gridfs.GridFS(db)

load_dotenv("../../../.env")
EMAIL = os.getenv("INSTAGRAM_EMAIL")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

profiles_list = list(collection_profiles.find())

updatePostCount = 0
insertPostCount = 0
errorPostCount = 0
errorMediaCount = 0
postCount = 0

# Função para upload de imagem
def upload_image(filename, url):
    file_path = os.path.join('../downloads', filename)

    # Criar diretório se não existir
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)

            existing_file = db.fs.files.find_one({'filename': filename})
            if existing_file:
                existing_file_id = existing_file['_id']
                fs.delete(existing_file_id)

            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_id = fs.put(file_data, filename=filename)

            if os.path.exists(file_path):
                os.remove(file_path)

            return f"http://localhost:5000/instagram/image/{file_id}"
        else:
            print(f"Falha ao baixar a imagem de {url}")
            return ''
    except Exception as e:
        print(f"Erro ao fazer upload da imagem: {e}")
        return ''

def get_medias(post, userid):
    medias = []
    mediaid = str(post.mediaid)
    if post.typename == "GraphSidecar":
        for i, sidecar in enumerate(post.get_sidecar_nodes(), start=1):
            try:
                medias.append({
                    'url': upload_image(
                        f'{mediaid}_{i}_display_url.jpg',
                        sidecar.display_url
                    ) if not sidecar.is_video else sidecar.video_url,
                    'isVideo': sidecar.is_video,
                })
            except Exception as e:
                print(e)
                errorMediaCount = errorMediaCount + 1
    else:
        try:
            medias.append({
                'url': upload_image(
                    f'{mediaid}_{0}_display_url.jpg',
                    post.url
                ) if post.typename == 'GraphImage' else post.video_url,
                'isVideo': post.is_video,
            })
        except Exception as e:
            print(e)
            errorMediaCount = errorMediaCount + 1

    query = {'mediaid': mediaid, 'userid': {'$ne': userid}}
    count = collection_posts.count_documents(query) > 0
    if count:
        collection_posts.update_many(query, {"$set": {"medias": medias}})

    return medias

L = instaloader.Instaloader()
L.login(EMAIL, PASSWORD)

for i, profile_doc in enumerate(profiles_list, start=1):
    username = profile_doc.get('username')
    userid = profile_doc.get('userid')

    print(f"extraindo publicações de {username}")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        posts = list(profile.get_posts())
    except Exception as e:
        if "checkpoint_required" in str(e) or "challenge_required" in str(e):
            print("Faça uma verificação manual no instagram para prosseguir")
            input("Pressione Enter para continuar...")
        elif "Please wait a few minutes before you try again" in str(e):
            time.sleep(5 * 60)
        else: 
            print(e)
        profile = instaloader.Profile.from_username(L.context, username)
        posts = list(profile.get_posts())

    error = 0

    if not posts:
        errorPostCount = errorPostCount + 1
        error = error + 1
        continue

    postCount = postCount + len(posts)

    datas = []
    for i, post in enumerate(posts, start=1):

        time.sleep(random.uniform(2.0, 7.0))

        print(f"loading... ({i}/{len(posts)})")

        time.sleep(random.uniform(0.5, 5.0))

        try:
            data = {
                'mediaid': str(post.mediaid),
                'caption': post.caption,
                'date': post.date,
                'likeCount': post.likes,
                'commentCount': post.comments,
                'isVideo': post.is_video,
                'duration': post.video_duration if post.video_duration is not None else 0,
                'videoViewCount': post.video_view_count if post.video_view_count is not None else 0,
                'userid': userid,
                'medias': get_medias(post, userid),
                'extraction': str(datetime.now()),
            }

            mediaid = data['mediaid']
            query = {
                'mediaid': mediaid,
                'userid': userid
            }
            if collection_posts.find_one(query):
                collection_posts.update_one(query, {"$set": data})
                updatePostCount = updatePostCount + 1
            else:
                collection_posts.insert_one(data)
                insertPostCount = insertPostCount + 1

        except Exception as e:
            if "checkpoint_required" in str(e) or "challenge_required" in str(e):
                print("Faça uma verificação manual no instagram para prosseguir")
                input("Pressione Enter para continuar...")
            elif "Please wait a few minutes before you try again" in str(e):
                time.sleep(5 * 60)
            else: 
                print(e)
            errorPostCount = errorPostCount + 1
            error = error + 1

    print('')
    print(f"Total: {len(posts)}")
    print(f'Erros: {error}')
    print(f"=======================================")
    print('')

    time.sleep(random.uniform(10.0, 20.0))

print(f"total de publicaçẽs: {postCount}")
print(f"{updatePostCount} publicalações atualizada")
print(f"{insertPostCount} publicações inserida")
print(f"{errorMediaCount} medias com erro")
print(f"{errorPostCount} publicações com erro")