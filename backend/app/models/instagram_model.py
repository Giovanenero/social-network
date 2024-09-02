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
    
    def get_posts(self, username, start, end):
        result = []
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            for post in profile.get_posts():
                data = {}
                data['shortcode'] = post.shortcode

                #post = instaloader.Post.from_shortcode(self.L.context, post.shortcode)

                data['isVideo'] = post.is_video
                if data['isVideo']:
                    data['duration'] = post.video_duration
                    data['url'] = post.video_url
                    data['viewCount'] = post.video_view_count
                else:
                    data['url'] = post.url

                data['caption'] = post.caption
                data['date'] = post.date
                data['commentsCount'] = post.comments
                data['likes'] = post.likes

                result.append(data)
        except Exception as e:
            print(f"erro ao coletar postagens de {username}: {e}")

        return result
    
    def get_comments(self, shortcode):
        result = []
        try:
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            for comment in post.get_comments():
                data = {}
                data['text'] = comment.text
                data['username'] = comment.owner.username
                data['date'] = comment.created_at_utc
                data['likesCount'] = comment.likes_count
                commenter_profile = instaloader.Profile.from_id(self.L.context, comment.owner.userid)
                data['url'] = commenter_profile.profile_pic_url

                data_answers = []
                for answer in post.answers:
                    #answer = instaloader.PostCommentAnswer(post.id, post.created_at_utc, post.text, post.owner, post.likes_count)
                    print(answer)
                    data_answer = {}
                    data_answer['date'] = answer.created_at_utc
                    data_answer['likesCount'] = answer.likes_count
                    data_answer['text'] = answer.text
                    data_answer['url'] = answer.owner.profile_pic_url
                    data_answer['unsername'] = answer.owner.unsername
                    data_answers.append(data_answer)

                data['answers'] = data_answers

                result.append(data)
        except Exception as e:
            print(f"erro ao coletar comentários {shortcode}: {e}")
        return result