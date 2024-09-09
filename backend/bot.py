import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from telegram.ext import CallbackQueryHandler
import os
from dotenv import load_dotenv
import instaloader
import requests
from pymongo import MongoClient
import gridfs
from datetime import datetime, timedelta
import random

from instagram_extraction import InstagramExtraction

load_dotenv("../.env")
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
EMAIL = os.getenv("INSTAGRAM_EMAIL")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

L = instaloader.Instaloader()

client = MongoClient('mongodb://localhost:27017/')
db = client['instagram']
collection_profiles = db['profiles']
collection_profiles.create_index('userid', unique=True)
collection_posts = db['posts']
collection_posts.create_index(['mediaid', 'userid'])
collection_statistics = db['statistics']
fs = gridfs.GridFS(db)

posts_processing = False
comments_processing = False
profiles_processing = False
MAX_ATTEMPTS = 5

pause_event = asyncio.Event()
pause_event.set()  # Start in a non-paused state

async def error(update, e, attempt):
    global posts_processing, comments_processing, profiles_processing
    if "checkpoint_required" in e or "challenge_required" in e:
        await update.message.reply_text("Verificação manual é necessária...")
    elif "Please wait a few minutes before you try again" in e:
        await update.message.reply_text("Espere alguns minutos antes de tentar novamente!")
    else:
        print(e)
    
    attempt += 1
    if int(attempt) < MAX_ATTEMPTS:
        await update.message.reply_text(f"Ocorreu um erro: {e}. Tentativa {attempt} de {MAX_ATTEMPTS}.")
        await asyncio.sleep(5*60)
    else:
        await update.message.reply_text(f"Falha após {MAX_ATTEMPTS} tentativas. A extração foi interrompida!")
        posts_processing = False
        profiles_processing = False
        comments_processing = False
    return attempt

async def comments_extraction(update):
    return

async def login(update):
    try:
        L.login(EMAIL, PASSWORD)
    except Exception as e:
        print(e)
        await update.message.reply_text(f"Erro ao fazer login")

def get_url(filename, url):
    file_path = os.path.join('downloads', filename)

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

async def get_profile(update, username):

    attempt = 0
    success = False

    while int(attempt) < MAX_ATTEMPTS and not success:
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            success = True
        except Exception as e:
            attempt = await error(update, str(e), attempt)
    return profile

def get_medias(post, userid):
    medias = []
    mediaid = str(post.mediaid)
    if post.typename == "GraphSidecar":
        for i, sidecar in enumerate(post.get_sidecar_nodes(), start=1):
            try:
                medias.append({
                    'url': get_url(
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
                'url': get_url(
                    f'{mediaid}_{0}_display_url.jpg',
                    post.url
                ) if post.typename == 'GraphImage' else post.video_url,
                'isVideo': post.is_video,
            })
        except Exception as e:
            print(e)

    query = {'mediaid': mediaid, 'userid': {'$ne': userid}}
    count = collection_posts.count_documents(query) > 0
    if count:
        collection_posts.update_many(query, {"$set": {"medias": medias}})

    return medias

async def posts_extraction(update: Update, context: CallbackContext) -> int:
    global posts_processing
    if posts_processing:
        await update.message.reply_text("A extração já está em andamento!")
        return

    posts_processing = True
    await update.message.reply_text("Iniciando a extração de publicações do Instagram...")
    
    await login(update)
    
    profiles_list = list(collection_profiles.find())

    for i, profile_doc in enumerate(profiles_list, start=1):
        if not posts_processing:
                return

        updatePostCount = 0
        insertPostCount = 0
        postCount = 0

        username = profile_doc.get('username')
        userid = profile_doc.get('userid')
        profile = await get_profile(update, username)
        posts = []

        attempt = 0
        success = False
        while int(attempt) < MAX_ATTEMPTS and not success:
            try:
                posts = list(profile.get_posts())
                success = True
            except Exception as e:
                attempt = await error(update, str(e), attempt)

        if not success:
            return

        if not posts:
            await update.message.reply_text(f"Não há nada para extrair de {username}")
            continue
            
        postCount += len(posts)

        for i, post in enumerate(posts, start=1):
            if not posts_processing:
                return

            print(f"loading... ({i}/{len(posts)})")
            await asyncio.sleep(random.uniform(2.0, 7.0))

            attempt = 0
            success = False

            while int(attempt) < MAX_ATTEMPTS and not success:
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
                        updatePostCount += 1
                    else:
                        collection_posts.insert_one(data)
                        insertPostCount += 1

                    success = True

                except Exception as e:
                    attempt = await error(update, e, attempt)
            
        await asyncio.sleep(random.uniform(10.0, 20.0))
        text = f"Extração de publicações de {username} foi concluída!\n"
        text += f"\ntotal: {postCount}"
        text += f"\natualizadas: {updatePostCount}"
        text += f"\ninseridas : {insertPostCount}"
        await update.message.reply_text(text)


    posts_processing = False
    await update.message.reply_text("Extração concluída!")
    return

async def profiles_extraction(update: Update, context: CallbackContext) -> int:
    global profiles_processing
    if profiles_processing:
        await update.message.reply_text("A extração já está em andamento!")
        return

    profiles_processing = True
    await update.message.reply_text("Iniciando a extração de dados de perfil de usuários do Instagram...")

    usernames = ['wise.bifor', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.cado', 'wise.systems']

    for username in usernames:
        if not profiles_processing:
            return

        profile = await get_profile(update, username)
        result = {}
        result['username'] = profile.username
        result['fullname'] = profile.full_name
        result['biography'] = profile.biography
        result['externalUrl'] = profile.external_url
        result['followers'] = profile.followers
        result['followees'] = profile.followees
        result['mediacount'] = profile.mediacount
        result['userid'] = str(profile.userid)
        result['extraction'] = str(datetime.now())
        result ['url'] = get_url(f'{username}_profile_pic.jpg', profile.profile_pic_url)

        query = {'username': username}
        if len(list(collection_profiles.find(query))) > 0:
            collection_profiles.update_one(query, {"$set": result})
            print("imagem atualizada no mongodb")
        else:
            collection_profiles.insert_one(result)
            print("imagem inserida no mongodb")

        await asyncio.sleep(random.uniform(10.0, 20.0))

    await update.message.reply_text("Extração de dados do perfil de usuários do Instagram foi finalizada!")

async def statistics_extraction(update: Update, context: CallbackContext) -> int:
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

    await update.message.reply_text("Registro de estatísticas de perfil e publicações do Instagram realizado com sucesso!")

async def cancel_extraction(update: Update, context: CallbackContext) -> int:
    global posts_processing, comments_processing, profiles_processing
    posts_processing = False
    comments_processing = False
    profiles_processing = False
    await update.message.reply_text("Extração de dados interrompida!")
    return

def main() -> None:
    application = Application.builder().token(TOKEN_TELEGRAM).build()

    application.add_handler(CommandHandler("posts", posts_extraction))
    application.add_handler(CommandHandler("profiles", profiles_extraction))
    application.add_handler(CommandHandler("statistics", statistics_extraction))
    #application.add_handler(CommandHandler("comments", comments_extraction))
    #application.add_handler(CommandHandler("continue", continue_extraction))
    application.add_handler(CommandHandler("cancel", cancel_extraction))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, continue_extraction))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()