from datetime import datetime
import random
import instaloader
import requests
import os
import time
from pymongo import MongoClient
import gridfs
from dotenv import load_dotenv

MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'instagram'
DOWNLOADS_DIR = '../downloads'
IMAGE_URL_PREFIX = "http://localhost:5000/instagram/image/"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection_comments = db['comments']
collection_posts = db['posts']
collection_profile = db['profiles']
fs = gridfs.GridFS(db)

collection_comments.create_index('commentId', unique=True)

load_dotenv("../../../.env")
EMAIL = os.getenv("INSTAGRAM_EMAIL")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

L = instaloader.Instaloader()
L.login(EMAIL, PASSWORD)

updateCommentCount = 0
insertCommentCount = 0
errorPost = 0
commentCount = 0

def upload_image(filename, url):
    file_path = os.path.join(DOWNLOADS_DIR, filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)

            existing_file = fs.find_one({'filename': filename})
            if existing_file:
                fs.delete(existing_file._id)

            with open(file_path, 'rb') as f:
                file_id = fs.put(f, filename=filename)

            os.remove(file_path)

            return f"{IMAGE_URL_PREFIX}{file_id}"
        else:
            print(f"Falha ao baixar a imagem de {url}")
            return ''
    except Exception as e:
        print(f"Erro ao fazer upload da imagem: {e}")
        return ''

def get_replies(answers):
    result = []
    for answer in answers:
        result.append({
            "date": answer.created_at_utc,
            "likesCount": answer.likes_count,
            "username": answer.owner.username if answer.owner else '',
            "text": answer.text,
            'url': upload_image(
                f'{answer.owner.userid}_profile_pic.jpg',
                answer.owner.get_profile_pic_url() if answer.owner else ''
            ) if answer.owner else '',
        })
    return result

posts = collection_posts.find()
posts_list = list(posts)

for i, post_doc in enumerate(posts_list, start=1):
    print(f"Publicação ({i}/{len(posts_list)})")

    mediaid = post_doc.get('mediaid')
    if not mediaid or not post_doc.get('commentCount'):
        continue

    try:
        post = instaloader.Post.from_mediaid(L.context, int(mediaid))
        commentCount += post.comments
        comments = list(post.get_comments())
        
        print('==========================================')

        for j, comment in enumerate(comments, start=1):
            print(f"Loading... ({j}/{len(comments)})")

            data = {
                "commentId": comment.id,
                'text': comment.text,
                'date': comment.created_at_utc,
                'likesCount': comment.likes_count,
                'username': comment.owner.username if comment.owner else '',
                'replies': get_replies(comment.answers),
                'mediaid': mediaid,
                'extraction': str(datetime.now()),
            }

            url = upload_image(
                f'{comment.owner.username}_profile_pic.jpg',
                comment.owner.profile_pic_url if comment.owner else ''
            )

            data['url'] = url

            if collection_comments.find_one({"commentId": data["commentId"]}):
                collection_comments.update_one({"commentId": data["commentId"]}, {"$set": data})
                updateCommentCount += 1
            else:
                collection_comments.insert_one(data)
                insertCommentCount += 1

            if collection_posts.count_documents({'username': data['username'], 'commentId': {'$ne': data['commentId']}}):
                collection_posts.update_many({'username': data['username']}, {"$set": {"url": url}})

            if collection_profile.count_documents({'username': data['username']}):
                collection_profile.update_one({'username': data['username']}, {'$set': {"url": url}})

            time.sleep(random.uniform(2.0, 7.0))
        print('==========================================')
    except Exception as e:
        if "checkpoint_required" in str(e) or "challenge_required" in str(e):
            print("Faça uma verificação manual no instagram para prosseguir")
            input("Pressione Enter para continuar...")
        elif "Please wait a few minutes" in str(e):
            time.sleep(5 * 60)
        else: 
            print(e)
        errorPost += 1

    time.sleep(random.uniform(10.0, 20.0))

print(f"=======================================")
print(f"Total de comentários: {commentCount}")
print(f"{updateCommentCount} comentários atualizados")
print(f"{insertCommentCount} comentários inseridos")
print(f"{errorPost} publicações com erros")
