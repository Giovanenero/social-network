import asyncio
import os
import random
import requests
import gridfs
import instaloader
from datetime import datetime, timedelta
from pymongo import MongoClient
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")
INSTALOADER_INSTANCES = 2
INSTAGRAM_EMAILS = [os.getenv(f"INSTAGRAM_EMAIL_{i + 1}") for i in range(INSTALOADER_INSTANCES)]
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

class Instagram:
    def __init__(self, update: Update):
        self.update = update
        self.client = MongoClient(MONGO_URI)
        self.db = self.client['instagram']
        self.collection_profiles = self.db['profiles']
        self.collection_posts = self.db['posts']
        self.collection_comments = self.db['comments']
        self.collection_statistics = self.db['statistics']
        self.fs = gridfs.GridFS(self.db)

        self.collection_profiles.create_index('userid', unique=True)
        self.collection_posts.create_index(['mediaid', 'userid'])

        self.index = 0
        self.L = None

    async def login(self, max_attempts=5):
        attempt = 0
        while attempt < max_attempts:
            try:
                L = instaloader.Instaloader()
                L.login(INSTAGRAM_EMAILS[self.index], INSTAGRAM_PASSWORD)
                self.L = L
                return True
            except Exception as e:
                await self.handle_login_error(e)
                attempt += 1
        return None

    async def handle_login_error(self, error):
        error_str = str(error)
        if "checkpoint_required" in error_str or "challenge_required" in error_str:
            await self.update.message.reply_text(f"Verificação manual é necessária para o {INSTAGRAM_EMAILS[self.index]}")
            await asyncio.sleep(300)
        elif "Please wait a few minutes before you try again" in error_str:
            self.index = (self.index + 1) % INSTALOADER_INSTANCES
            await self.login()
            await self.update.message.reply_text(f"Muitas tentativas. Mudando para {INSTAGRAM_EMAILS[self.index]}")
        else:
            await self.update.message.reply_text(f"Erro inesperado: {error_str}")

    async def fetch_url(self, filename, url):
        file_path = os.path.join('downloads', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)

                if (existing_file := self.db.fs.files.find_one({'filename': filename})):
                    self.fs.delete(existing_file['_id'])

                with open(file_path, 'rb') as file:
                    file_id = self.fs.put(file.read(), filename=filename)

                os.remove(file_path)
                return f"http://localhost:5000/instagram/image/{file_id}"
            else:
                logger.error("Falha ao baixar a imagem de %s", url)
                return ''
        except Exception as e:
            logger.error("Erro ao fazer upload da imagem: %s", e)
            return ''

    async def fetch_medias(self, post, userid):
        medias = []
        mediaid = str(post.mediaid)
        if post.typename == "GraphSidecar":
            for i, sidecar in enumerate(post.get_sidecar_nodes(), start=1):
                try:
                    medias.append({
                        'url': await self.fetch_url(f'{mediaid}_{i}_display_url.jpg', sidecar.display_url)
                        if not sidecar.is_video else sidecar.video_url,
                        'isVideo': sidecar.is_video,
                    })
                except Exception as e:
                    logger.error("Erro ao processar sidecar: %s", e)
        else:
            try:
                medias.append({
                    'url': await self.fetch_url(
                        f'{mediaid}_{0}_display_url.jpg', post.url
                    ) if post.typename == 'GraphImage' else post.video_url,
                    'isVideo': post.is_video,
                })
            except Exception as e:
                logger.error("Erro ao processar imagem ou vídeo: %s", e)

        query = {'mediaid': mediaid, 'userid': {'$ne': userid}}
        if self.collection_posts.count_documents(query) > 0:
            self.collection_posts.update_many(query, {"$set": {"medias": medias}})

        return medias

    async def fetch_profile(self, username, max_attempts=3):
        attempt = 0
        while attempt < max_attempts:
            try:
                return instaloader.Profile.from_username(self.L.context, username)
            except Exception as e:
                await self.handle_login_error(e)
                attempt += 1
        return None

    async def extract_profiles(self):
        usernames = ['wise.systems', 'wise.cado', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.bifor']
        update_count, insert_count, profile_count = 0, 0, 0

        for username in usernames:
            profile_count += 1
            profile_obj = await self.fetch_profile(username)

            if profile_obj is None:
                continue

            attempt, success = 0, False
            while attempt < 3 and not success:
                try:
                    result = {
                        "username": profile_obj.username,
                        "fullname": profile_obj.full_name,
                        "biography": profile_obj.biography,
                        "followers": profile_obj.followers,
                        "followees": profile_obj.followees,
                        "mediacount": profile_obj.mediacount,
                        "userid": str(profile_obj.userid),
                        "url": await self.fetch_url(f'{username}_profile_pic.jpg', profile_obj.profile_pic_url),
                        "extraction": str(datetime.now())
                    }
                    success = True
                except Exception as e:
                    await self.handle_login_error(e)
                    attempt += 1

            if result:
                if self.collection_profiles.find_one({'username': username}):
                    self.collection_profiles.update_one({'username': username}, {"$set": result})
                    update_count += 1
                else:
                    self.collection_profiles.insert_one(result)
                    insert_count += 1
            else:
                await self.update.message.reply_text(f"Não foi possível extrair o perfil de {username}")

            await asyncio.sleep(random.uniform(30.0, 60.0))

        summary = (f"Extração de perfil do Instagram finalizada com sucesso!\n"
                   f"Total: {profile_count}\n"
                   f"Atualizado: {update_count}\n"
                   f"Inserido: {insert_count}")
        await self.update.message.reply_text(summary)

    async def fetch_posts(self, username, max_attempts=3):
        attempt = 0
        while attempt < max_attempts:
            try:
                profile = await self.fetch_profile(username)
                if profile is not None:
                    return list(profile.get_posts())
                return None
            except Exception as e:
                await self.handle_login_error(e)
                attempt += 1
        return None

    async def extract_post(self, mediaid, userid, max_attempts=5):
        attempt, update_posts, insert_posts = 0, 0, 0
        while attempt < max_attempts:
            try:
                post = await self.fetch_post(mediaid)
                data = {
                    'mediaid': str(post.mediaid),
                    'caption': post.caption,
                    'date': post.date,
                    'likeCount': post.likes,
                    'commentCount': post.comments,
                    'isVideo': post.is_video,
                    'duration': post.video_duration if post.video_duration else 0,
                    'videoViewCount': post.video_view_count if post.video_view_count else 0,
                    'userid': userid,
                    'medias': await self.fetch_medias(post, userid),
                    'extraction': str(datetime.now()),
                }

                query = {'mediaid': data['mediaid'], 'userid': userid}
                if self.collection_posts.find_one(query):
                    self.collection_posts.update_one(query, {"$set": data})
                    update_posts += 1
                else:
                    self.collection_posts.insert_one(data)
                    insert_posts += 1

                return update_posts, insert_posts

            except Exception as e:
                await self.handle_login_error(e)
                attempt += 1
            return update_posts, insert_posts

    async def extract_posts(self):
        profiles_list = list(self.collection_profiles.find())

        for profile_doc in profiles_list:
            username = profile_doc.get('username')
            userid = profile_doc.get('userid')

            posts = await self.fetch_posts(username)
            if posts is None:
                continue

            mediaids = [post.mediaid for post in posts]

            update_posts, insert_posts, post_count = 0, 0, len(posts)

            for i, mediaid in enumerate(mediaids, start=1):
                await self.update.message.reply_text(f"{username}: carregando... ({i}/{post_count})")

                update, insert = await self.extract_post(mediaid, userid)
                update_posts += update
                insert_posts += insert
                
                #await asyncio.sleep(random.uniform(3500.0, 3700.0))
                await asyncio.sleep(random.uniform(300.0, 600.0))

            summary = (f"Extração de publicações de {username} concluída!\n"
                       f"Total: {post_count}\n"
                       f"Atualizadas: {update_posts}\n"
                       f"Inseridas: {insert_posts}")
            await self.update.message.reply_text(summary)

    def extract_statistics(self):
        profiles = list(self.collection_profiles.find())

        date_today = str(datetime.today().date())

        for profile in profiles:
            userid = profile['userid']
            posts = list(self.collection_posts.find({'userid': userid}))
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
            statistics = list(self.collection_statistics.find({'userid': userid}))
            self.collection_statistics.update_one(query, {"$set": data}, upsert=True)

                
        date_30_days_ago = datetime.fromisoformat(date_today) - timedelta(days=30)
        date_30_days_ago = date_30_days_ago.date()
        statistics = list(self.collection_statistics.find())
        for statistic in statistics:
            if date_30_days_ago > datetime.fromisoformat(statistic['date']).date():
                self.collection_statistics.delete_one({'date': statistic['date']}) 

    async def fetch_post(self, mediaid, max_attempt = 5):
        attempt = 0
        while attempt < max_attempt:
            try:
                return instaloader.Post.from_mediaid(self.L.context, int(mediaid))
            except Exception as e:
                attempt += 1
                await self.handle_login_error(e)
        return None

    async def fetch_comments(self, post, max_attempt = 3):
        attempt = 0
        while attempt < max_attempt:
            try:
                return list(post.get_comments())
            except Exception as e:
                attempt += 1
                await self.handle_login_error(e)
        return None

    async def fetch_replies(self, answers, max_attempt = 5):
        result = []
        for answer in answers:
            attempt = 0
            success = False
            while attempt < max_attempt and not success:
                try:
                    owner = answer.owner
                    result.append({
                        "date": answer.created_at_utc,
                        "likesCount": answer.likes_count,
                        "username": owner.username if owner else '',
                        "text": answer.text,
                        'url': await self.fetch_url(
                            f'{owner.userid}_profile_pic.jpg',
                            owner.get_profile_pic_url() if owner else ''
                        ) if owner else '',
                    })
                    success = True
                except Exception as e:
                    attempt += 1
                    await self.handle_login_error(e)
        return result

    async def extract_comments(self):
        query = {"commentCount": {"$gt": 0}}
        posts = self.collection_posts.find(query)
        posts_list = list(posts)

        update_comments, insert_comments, total_comments = 0, 0, 0

        for i, post_doc in enumerate(posts_list, start=1):
            await self.update.message.reply_text(f"Publicação ({i}/{len(posts_list)})")

            mediaid = post_doc.get('mediaid')
            if not mediaid or not post_doc.get('commentCount'):
                continue
                
            post = await self.fetch_post(mediaid)
            if post is None:
                continue

            total_comments += post.comments
            await asyncio.sleep(random.uniform(30.0, 60.0))
            comments = await self.fetch_comments(post)
            if comments is None:
                continue
            
            await asyncio.sleep(random.uniform(30.0, 60.0))

            attempt = 0
            success = False
            while attempt < 5 and not success:
                try:
                    for j, comment in enumerate(comments, start=1):
                        await self.update.message.reply_text(f"Carregando... ({j}/{len(comments)})")
                        
                        answers = list(comment.answers)
                        owner = comment.owner
                        await asyncio.sleep(random.uniform(30.0, 60.0))
                        
                        data = {
                            "commentId": comment.id,
                            'text': comment.text,
                            'date': comment.created_at_utc,
                            'likesCount': comment.likes_count,
                            'username': owner.username if owner else '',
                            'replies': await self.fetch_replies(answers) if len(answers) else [],
                            'mediaid': mediaid,
                            'url': await self.fetch_url(
                                f'{owner.username}_profile_pic.jpg',
                                owner.profile_pic_url if owner else ''
                            ),
                            'extraction': str(datetime.now()),
                        }

                        query = {'commentId': data['commentId']}
                        if self.collection_comments.find_one(query):
                            self.collection_comments.update_one(query, {"$set": data})
                            update_comments += 1
                        else:
                            self.collection_comments.insert_one(data)
                            insert_comments += 1

                        # if collection_posts.count_documents({'username': data['username'], 'commentId': {'$ne': data['commentId']}}):
                        #     collection_posts.update_many({'username': data['username']}, {"$set": {"url": url}})

                        # if collection_profile.count_documents({'username': data['username']}):
                        #     collection_profile.update_one({'username': data['username']}, {'$set': {"url": url}})

                        await asyncio.sleep(random.uniform(300.0, 600.0))
                    success = True
                except Exception as e:
                    attempt += 1
                    await self.handle_login_error(e)

            await asyncio.sleep(random.uniform(600.0, 800.0))
        

        text = f"Extração de comentários e respostas de comentários do Instagram foi concluída!\n"
        text += f"\ntotal: {total_comments}"
        text += f"\natualizadas: {update_comments}"
        text += f"\ninseridas : {insert_comments}"
        await self.update.message.reply_text(text)
        return