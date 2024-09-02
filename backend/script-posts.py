from datetime import datetime
import instaloader
import requests
import os
from pymongo import MongoClient
import gridfs
from dotenv import load_dotenv

client = MongoClient('mongodb://localhost:27017/')
db = client['instagram']
collection_posts = db['posts']
collection_comments = db['comments']
collection_posts.create_index('mediaid', unique=True)
collection_comments.create_index('commentId', unique=True)

#fs = gridfs.GridFS(db)

usernames = ['wise.bifor', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.cado', 'wise.systems']
L = instaloader.Instaloader()

load_dotenv("../.env")
EMAIL = os.getenv("INSTAGRAM_EMAIL")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

L.login(EMAIL, PASSWORD)

#for username in usernames:
#    profile = instaloader.Profile.from_username(L.context, username)
#    posts = profile.get_posts()

profile = instaloader.Profile.from_username(L.context, "wise.archival")
posts = profile.get_posts()

result = {}

erros_posts = 0
erros_comments = 0

for post in posts:
    result = {
        'mediaid': str(post.mediaid),
        'caption': post.caption,
        'commentsCount': post.comments,
        'date': post.date,
        'likesCount': post.likes,
        'isVideo': post.is_video,
        'duration': post.video_duration if post.video_duration is not None else 0,
        'videoViewCount': post.video_view_count if post.video_view_count is not None else 0,
        'medias': []
    }

    if post.typename == "GraphSidecar":
        for sidecar in post.get_sidecar_nodes():
            result['medias'].append({
                "url": sidecar.video_url if sidecar.is_video else sidecar.display_url,
                "isVideo": sidecar.is_video
            })

    comments = []
    commentsId = []
    for comment in post.get_comments():
        commentsId.append(comment.id)
        comments.append({
            "commentId": comment.id,
            'text': comment.text,
            'date': comment.created_at_utc,
            'likesCount': comment.likes_count,
            'username': comment.owner.username if comment.owner else '',
            'url': comment.owner.profile_pic_url if comment.owner else '',
            'replies': [
                {
                    "date": answer.created_at_utc,
                    "likesCount": answer.likes_count,
                    "username": answer.owner.username if answer.owner else '',
                    "text": answer.text,
                    "url": answer.owner.get_profile_pic_url() if answer.owner else ''
                }
                for answer in comment.answers
            ],
            'extraction': str(datetime.now())
        })
    
    result["commentsId"] = commentsId
    result['extraction'] = str(datetime.now())

    try:
        query = {"mediaid": result['mediaid']}
        if collection_posts.find_one(query):
            collection_posts.update_one(query, {"$set": result})
            print(f"Post {result['mediaid']} atualizado")
        else:
            collection_posts.insert_one(result)
            print(f"Post {result['mediaid']} inserido")

    except Exception as e:
        print(f"Erro ao inserir/atualizar o post {result['mediaid']}: {e}")
        erros_posts += erros_posts

    try:
        for comment in comments:
            query = {"commentId": comment['commentId']}
            if collection_comments.find_one(query):
                collection_comments.update_one(query, {"$set": comment})
                print(f"Comentário {comment['commentId']} atualizado")
            else:
                collection_comments.insert_one(comment)
                print(f"Comentário {comment['commentId']} inserido")
    except Exception as e:
        print(f"erro ao inserir/atualizar o comentário {comment['commentId']}: {e}")
        erros_comments += erros_comments

print(f"\nQuantidade de publicações com erros: {erros_posts}")
print(f"Quantidade de comentários com erros: {erros_comments}")





