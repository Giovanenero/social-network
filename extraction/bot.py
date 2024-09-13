import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import os
import instaloader
import requests
from pymongo import MongoClient
import gridfs
from datetime import datetime, timedelta
import random

TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['instagram']
collection_profiles = db['profiles']
collection_profiles.create_index('userid', unique=True)
collection_posts = db['posts']
collection_posts.create_index(['mediaid', 'userid'])
collection_statistics = db['statistics']
collection_comments = db['comments']
collection_comments.create_index('commentId', unique=True)
fs = gridfs.GridFS(db)

INSTALOADER_INSTANCES = 2
INSTAGRAM_EMAILS = [os.getenv(f"INSTAGRAM_EMAIL_{i + 1}") for i in range(INSTALOADER_INSTANCES)]
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
L = [None] * INSTALOADER_INSTANCES
MAX_ATTEMPTS = 5

async def login(update: Update):
    global L
    count = 0
    for i in range(INSTALOADER_INSTANCES):
        try:
            L[i] = instaloader.Instaloader()
            L[i].login(INSTAGRAM_EMAILS[i], INSTAGRAM_PASSWORD)
            await update.message.reply_text(f"Login com {INSTAGRAM_EMAILS[i]} realizado com sucesso!")
            count += 1
        except Exception as e:
            await update.message.reply_text(f"Erro ao realizar login com {INSTAGRAM_EMAILS[i]}")
            print(f"Erro ao fazer login: {e}")

    await update.message.reply_text(f"{count} login(s) realizado(s) com sucesso!")

async def error(update, e, attempt, email):
    e = str(e)
    if "checkpoint_required" in e or "challenge_required" in e:
        await update.message.reply_text(f"Verificação manual é necessária para o {email}")
    elif "Please wait a few minutes before you try again" in e:
        await update.message.reply_text("Espere alguns minutos antes de tentar novamente!")
    else:
        print(f"Erro: {e}")

    attempt += 1
    if attempt < MAX_ATTEMPTS:
        await update.message.reply_text(f"Ocorreu um erro: {e}. Tentativa {attempt} de {MAX_ATTEMPTS}.")
        await asyncio.sleep(300.0)
    else:
        await update.message.reply_text(f"Falha após {MAX_ATTEMPTS} tentativas. A extração foi interrompida!")
    return attempt

async def get_replies(update: Update, email, answers):
    result = []
    for answer in answers:
        attempt = 0
        success = False
        while attempt < MAX_ATTEMPTS and not success:
            try:
                owner = answer.owner
                result.append({
                    "date": answer.created_at_utc,
                    "likesCount": answer.likes_count,
                    "username": owner.username if owner else '',
                    "text": answer.text,
                    'url': await get_url(
                        f'{owner.userid}_profile_pic.jpg',
                        owner.get_profile_pic_url() if owner else ''
                    ) if owner else '',
                })
                success = True
            except Exception as e:
                attempt = await error(update, e, attempt, email)
    return result

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

async def get_profile(update, username, index):
    global L
    attempt = 0
    success = False

    while int(attempt) < MAX_ATTEMPTS and not success:
        try:
            profile = instaloader.Profile.from_username(L[index%2].context, username)
            success = True
        except Exception as e:
            attempt = await error(update, e, attempt, INSTAGRAM_EMAILS[index%2])
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
    await update.message.reply_text("Iniciando a extração de publicações do Instagram...")
    
    #await init_instaloader(update)
    await login(update)
    
    profiles_list = list(collection_profiles.find())

    for i, profile_doc in enumerate(profiles_list, start=1):

        updatePostCount = 0
        insertPostCount = 0
        postCount = 0

        username = profile_doc.get('username')
        userid = profile_doc.get('userid')
        profile = await get_profile(update, username, i)
        posts = []

        attempt = 0
        success = False
        while attempt < MAX_ATTEMPTS and not success:
            try:
                posts = list(profile.get_posts())
                success = True
            except Exception as e:
                attempt = await error(update, e, attempt, INSTAGRAM_EMAILS[i%2])

        if not success:
            return

        if not posts:
            await update.message.reply_text(f"Não há nada para extrair de {username}")
            continue
            
        postCount += len(posts)

        for i, post in enumerate(posts, start=1):

            await update.message.reply_text(f"{username}: loading... ({i}/{len(posts)})")
            await asyncio.sleep(random.uniform(10.0, 20.0))

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
                    attempt = await error(update, e, attempt, INSTAGRAM_EMAILS[i%2])

            await asyncio.sleep(random.uniform(300.0, 600.0))
            
        await asyncio.sleep(random.uniform(600.0, 800.0))
        text = f"Extração de publicações de {username} foi concluída!\n"
        text += f"\ntotal: {postCount}"
        text += f"\natualizadas: {updatePostCount}"
        text += f"\ninseridas : {insertPostCount}"
        await update.message.reply_text(text)

    await update.message.reply_text("Extração concluída!")
    return

async def profiles_extraction(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Iniciando a extração de dados de perfil de usuários do Instagram...")
    await login(update)

    usernames = ['wise.bifor', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.cado', 'wise.systems']

    for i, username in enumerate(usernames, start=1):

        profile = await get_profile(update, username, i)
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

        await asyncio.sleep(random.uniform(15.0, 30.0))
        await update.message.reply_text(f"Extração de {username} concluída!")

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

async def comments_extraction(update: Update, context: CallbackContext) -> int:

    await update.message.reply_text("Iniciando a extração de comentários e respostas de comentários do Instagram...")

    query = {"commentCount": {"$gt": 0}}
    posts = collection_posts.find(query)
    posts_list = list(posts)

    updateComments = 0
    InsertComments = 0
    totalComments = 0

    await login(update)

    for i, post_doc in enumerate(posts_list, start=1):
        print(f"Publicação ({i}/{len(posts_list)})")

        email = INSTAGRAM_EMAILS[i%INSTALOADER_INSTANCES]

        mediaid = post_doc.get('mediaid')
        if not mediaid or not post_doc.get('commentCount'):
            continue
        
        attempt = 0
        success = False
        post = None
        while attempt < MAX_ATTEMPTS and not success:
            try:
                post = instaloader.Post.from_mediaid(L[i % INSTALOADER_INSTANCES].context, int(mediaid))
                success = True
            except Exception as e:
                attempt = await error(update, e, attempt, email)

        if post is None:
            continue

        totalComments += post.comments

        await asyncio.sleep(random.uniform(30.0, 60.0))

        attempt = 0
        success = False
        while attempt < MAX_ATTEMPTS and not success:
            try:
                comments = list(post.get_comments())
                success = True
            except Exception as e:
                attempt = await error(update, e, attempt, email)
        
        if comments is None:
            continue
        
        await asyncio.sleep(random.uniform(30.0, 60.0))
        print('==========================================')

        attempt = 0
        success = False
        while attempt < MAX_ATTEMPTS and not success:
            try:
                for j, comment in enumerate(comments, start=1):
                    print(f"Loading... ({j}/{len(comments)})")
                    answers = list(comment.answers)
                    owner = comment.owner
                    await asyncio.sleep(random.uniform(30.0, 60.0))
                    
                    data = {
                        "commentId": comment.id,
                        'text': comment.text,
                        'date': comment.created_at_utc,
                        'likesCount': comment.likes_count,
                        'username': owner.username if owner else '',
                        'replies': await get_replies(update, email, answers) if len(answers) else [],
                        'mediaid': mediaid,
                        'extraction': str(datetime.now()),
                    }

                    await asyncio.sleep(random.uniform(30.0, 60.0))

                    url = get_url(
                        f'{owner.username}_profile_pic.jpg',
                        owner.profile_pic_url if owner else ''
                    )

                    data['url'] = url

                    # if collection_comments.find_one({"commentId": data["commentId"]}):
                    #     collection_comments.update_one({"commentId": data["commentId"]}, {"$set": data})
                    #     updateCommentCount += 1
                    # else:
                    #     collection_comments.insert_one(data)
                    #     insertCommentCount += 1

                    # if collection_posts.count_documents({'username': data['username'], 'commentId': {'$ne': data['commentId']}}):
                    #     collection_posts.update_many({'username': data['username']}, {"$set": {"url": url}})

                    # if collection_profile.count_documents({'username': data['username']}):
                    #     collection_profile.update_one({'username': data['username']}, {'$set': {"url": url}})

                    query = {'commentId': data['commentId']}
                    if collection_comments.find_one(query):
                        collection_comments.update_one(query, {"$set": data})
                        updateComments += 1
                    else:
                        collection_comments.insert_one(data)
                        InsertComments += 1

                    await asyncio.sleep(random.uniform(300.0, 600.0))
                
                print('==========================================')
                success = True
            except Exception as e:
                attempt = await error(update, e, attempt, email)

        await asyncio.sleep(random.uniform(600.0, 800.0))
    

    text = f"Extração de comentários e respostas de comentários do Instagram foi concluída!\n"
    text += f"\ntotal: {totalComments}"
    text += f"\natualizadas: {updateComments}"
    text += f"\ninseridas : {InsertComments}"
    await update.message.reply_text(text)
    return

def main() -> None:
    application = Application.builder().token(TOKEN_TELEGRAM).build()

    application.add_handler(CommandHandler("posts", posts_extraction))
    application.add_handler(CommandHandler("profiles", profiles_extraction))
    application.add_handler(CommandHandler("statistics", statistics_extraction))
    application.add_handler(CommandHandler("comments", comments_extraction))
    #application.add_handler(CommandHandler("continue", continue_extraction))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, continue_extraction))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()