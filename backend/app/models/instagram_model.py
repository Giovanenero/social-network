from datetime import datetime
from flask import send_file
import instaloader
from dotenv import load_dotenv
import os

from app.models.mongodbclient import mongodbclient

class instagram_model:
    def __init__(self):
        L = instaloader.Instaloader()
        self.L = L
        self.usernames = ['wise.bifor', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.cado', 'wise.systems']
        load_dotenv("../../.env")
        self.email = os.getenv("INSTAGRAM_EMAIL")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        #self.download_directory = 'downloads'
        # if not os.path.exists(self.download_directory):
        #     os.makedirs(self.download_directory)

    def login(self):

        try:
            self.L.login(self.email, self.password)
            print('login realizado com sucesso')
        except instaloader.exceptions.BadCredentialsException:
            print("Credenciais inválidas. Verifique seu nome de usuário e senha.")
        except instaloader.exceptions.ConnectionException:
            print("Erro de conexão. Verifique sua conexão com a internet.")

    def get_profile(self, username):
        try:
            client = mongodbclient('instagram', 'profiles')
            profile = client.find('username', username)[0]
            profile.pop('_id', None)
            return profile
        except Exception as e:
            print(f"erro ao coletar informações do perfil de {username}: {e}")
        return {}
    
    def get_profiles(self):
        profiles = []
        for username in self.usernames:
            try:
                data = self.get_profile(username)
                profiles.append(data)
            except Exception as e:
                print(f"não foi possível obter dados de {username}: {e}")
        return profiles    
    
    def get_posts(self, userid, skip, limit):
        result = []
        try:
            client = mongodbclient('instagram', 'posts')
            posts = client.find('userid', userid, skip, limit)
            return posts
        except Exception as e:
            print(f"erro ao coletar postagens de {userid}: {e}")

        return result
    

    def get_metrics(self, userid, last_posts = 5):

        client = mongodbclient('instagram', 'posts')
        profile = mongodbclient('instagram', 'profiles').find('userid', userid)[0]

        followers = profile['followers']

        posts = list(client.find('userid', userid))

        totalLikes = 0
        totalComments = 0
        totalVideos = 0
        totalDuration = 0

        for post in posts:
            totalLikes += post['likeCount']
            totalComments += post['commentCount']
            totalVideos += 1 if post['isVideo'] else 0
            totalDuration += post['duration']

        i = 0
        last = []
        while(i < last_posts and len(post) > i):
            likes = posts[i]['likeCount']
            comments = posts[i]['commentCount']
            interactions = likes + comments
            last.append({
                'likes': likes,
                'comments': comments,
                'engagement': (interactions / followers) * 100
            })
        
        interactions = totalLikes + totalComments
        engagement_rate = ( interactions / followers ) * 100 if followers else 0

        return {
            'likesCount': totalLikes,
            'commentsCount': totalComments,
            'lastPosts': last,
            'interactions': interactions,
            'engagementRate': engagement_rate
        }



    
    def get_comments(self, mediaid):
        result = []
        try:
            client = mongodbclient('instagram', 'comments')
            comments = list(client.find('mediaid', mediaid))    
            return comments
        except Exception as e:
            print(f"erro ao coletar comentários {mediaid}: {e}")
        return result