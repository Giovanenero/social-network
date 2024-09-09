import asyncio
import random
from typing import Optional
import instaloader
import requests
from pymongo import MongoClient
import gridfs
from datetime import datetime
import os
from dotenv import load_dotenv

from telegram import Update

load_dotenv("../.env")
EMAIL = os.getenv("INSTAGRAM_EMAIL")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

class InstagramExtraction:
    def __init__(self, update: Update):
        self.update = update
        self.L = instaloader.Instaloader()
        self.processing = True
        self.cancel_event = asyncio.Event()

        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['instagram']
        self.collection_profiles = self.db['profiles']
        self.collection_posts = self.db['posts']
        self.collection_posts.create_index(['mediaid', 'userid'])
        self.fs = gridfs.GridFS(self.db)

    async def login(self):
        try:
            self.L.login(EMAIL, PASSWORD)
        except Exception as e:
            print(e)
            await self.update.message.reply_text(f"Erro ao fazer login")
            self.processing = False

    def get_url(self, filename, url):
        file_path = os.path.join('downloads', filename)

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                existing_file = self.db.fs.files.find_one({'filename': filename})
                if existing_file:
                    existing_file_id = existing_file['_id']
                    self.fs.delete(existing_file_id)

                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    file_id = self.fs.put(file_data, filename=filename)

                if os.path.exists(file_path):
                    os.remove(file_path)

                return f"http://localhost:5000/instagram/image/{file_id}"
            else:
                print(f"Falha ao baixar a imagem de {url}")
                return ''
        except Exception as e:
            print(f"Erro ao fazer upload da imagem: {e}")
            return ''

    async def pause(self, text):
        await self.update.message.reply_text(text)
        await self.cancel_event.wait()

    def cancel(self):
        self.processing = False
        self.cancel_event.set()

    async def get_profile(self, username):
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
        except Exception as e:
            if "checkpoint_required" in str(e) or "challenge_required" in str(e):
                await self.pause("Verificação manual é necessária...")
            elif "Please wait a few minutes before you try again" in str(e):
                await self.pause("Espere um pouco...")
            else: 
                print(e)
            profile = instaloader.Profile.from_username(self.L.context, username)
        return profile

    def get_medias(self, post, userid):
        medias = []
        mediaid = str(post.mediaid)
        if post.typename == "GraphSidecar":
            for i, sidecar in enumerate(post.get_sidecar_nodes(), start=1):
                try:
                    medias.append({
                        'url': self.get_url(
                            f'{mediaid}_{i}_display_url.jpg',
                            sidecar.display_url
                        ) if not sidecar.is_video else sidecar.video_url,
                        'isVideo': sidecar.is_video,
                    })
                except Exception as e:
                    print(e)
        else:
            try:
                medias.append({
                    'url': self.get_url(
                        f'{mediaid}_{0}_display_url.jpg',
                        post.url
                    ) if post.typename == 'GraphImage' else post.video_url,
                    'isVideo': post.is_video,
                })
            except Exception as e:
                print(e)

        query = {'mediaid': mediaid, 'userid': {'$ne': userid}}
        count = self.collection_posts.count_documents(query) > 0
        if count:
            self.collection_posts.update_many(query, {"$set": {"medias": medias}})

        return medias

    async def posts_extraction(self):
        await self.login()

        if not self.processing:
            return

        profiles_list = list(self.collection_profiles.find())

        for i, profile_doc in enumerate(profiles_list, start=1):
            if not self.processing:
                return

            updatePostCount = 0
            insertPostCount = 0
            errorPostCount = 0
            postCount = 0

            username = profile_doc.get('username')
            userid = profile_doc.get('userid')
            profile = await self.get_profile(username)
            posts = list(profile.get_posts())

            if not posts:
                await self.update.message.reply_text(f"Não há nada para extrair de {username}")
                continue
            
            postCount += len(posts)

            for i, post in enumerate(posts, start=1):
                if not self.processing:
                    return

                await asyncio.sleep(random.uniform(2.0, 7.0))
                print(f"loading... ({i}/{len(posts)})")
                await asyncio.sleep(random.uniform(0.5, 5.0))

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
                        'medias': self.get_medias(post, userid),
                        'extraction': str(datetime.now()),
                    }

                    mediaid = data['mediaid']
                    query = {
                        'mediaid': mediaid,
                        'userid': userid
                    }
                    if self.collection_posts.find_one(query):
                        self.collection_posts.update_one(query, {"$set": data})
                        updatePostCount += 1
                    else:
                        self.collection_posts.insert_one(data)
                        insertPostCount += 1

                except Exception as e:
                    if "checkpoint_required" in str(e) or "challenge_required" in str(e):
                        await self.pause("Verificação manual é necessária...")
                    elif "Please wait a few minutes before you try again" in str(e):
                        await self.pause("Verificação manual é necessária...") 
                    
                    errorPostCount += 1
            
            await asyncio.sleep(random.uniform(10.0, 20.0))
            text = f"Extração de publicações de {username} foi concluída!\n"
            text += f"\ntotal: {postCount}"
            text += f"\nerro: {errorPostCount}"
            text += f"\natualizadas: {updatePostCount}"
            text += f"\ninseridas : {insertPostCount}"
            await self.update.message.reply_text(text)
