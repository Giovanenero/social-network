from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

from app.models.mongodbclient import mongodbclient

class instagram_model:
    def __init__(self):
        self.usernames = ['wise.bifor', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.cado', 'wise.systems']

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
            posts = client.find('userid', userid, skip, limit, sort_name="date", ascending=False)
            return posts
        except Exception as e:
            print(f"erro ao coletar postagens de {userid}: {e}")

        return result
    
    def prediction_post(self, posts):
        df = pd.DataFrame(posts)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')

        df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month

        features_comments = ['days_since_start', 'day_of_week', 'month', 'isVideo', 'videoViewCount', 'duration']
        X_comments = df[features_comments]
        features_comments.append('commentCount')
        X_likes = df[features_comments]
        y_likes = df['likeCount']
        y_comments = df['commentCount']

        X_train_likes, X_test_likes, y_train_likes, y_test_likes = train_test_split(X_likes, y_likes, test_size=0.25, random_state=0)
        X_train_comments, X_test_comments, y_train_comments, y_test_comments = train_test_split(X_comments, y_comments, test_size=0.25, random_state=0)

        model_likes_rf = RandomForestRegressor(n_estimators=500, max_depth=4, random_state=0)
        model_comments_rf = RandomForestRegressor(n_estimators=500, max_depth=4, random_state=0)

        model_likes_rf.fit(X_train_likes, y_train_likes)
        model_comments_rf.fit(X_train_comments, y_train_comments)

        #y_pred_likes_rf = model_likes_rf.predict(X_test_likes)
        #y_pred_comments_rf = model_comments_rf.predict(X_test_comments)
        #print("MSE para Likes (Random Forest):", mean_squared_error(y_test_likes, y_pred_likes_rf))
        #print("MSE para Comentários (Random Forest):", mean_squared_error(y_test_comments, y_pred_comments_rf))

        next_data_likes = pd.DataFrame({
            'days_since_start': [df['days_since_start'].max() + 1],
            'day_of_week': [df['day_of_week'].mode()[0]],
            'month': [df['month'].mode()[0]],
            'isVideo': False,
            'videoViewCount': 0,
            'duration': 0,
            'commentCount': 0
        })

        predicted_likes_rf = model_likes_rf.predict(next_data_likes)
        predicted_comments_rf = model_comments_rf.predict(next_data_likes.drop(columns=['commentCount']))
        pred_likes = round(predicted_likes_rf[0])
        pred_comments = round(predicted_comments_rf[0])

        followers = list(mongodbclient('instagram', 'profiles').find('userid', '5532940513'))[0]['followers']

        #print(f"Previsão para a próxima publicação (Random Forest):")
        #print(f"Likes: {pred_likes}")
        #print(f"Comentários: {pred_comments}")
        #print(f"Interações: {pred_likes + pred_comments}")
        #print(f"Engajamento: {(((pred_likes + pred_comments) / followers) * 100):.3}%")

        return {
            'likeCount': pred_likes,
            'commentCount': pred_comments,
            'engajament': ((pred_likes + pred_comments) / followers) * 100
        }
    

    def get_metrics(self, userid, last_posts = 5):

        try:
            posts = list(mongodbclient('instagram', 'posts').find('userid', userid, sort_name="date", ascending=False))
            profile = mongodbclient('instagram', 'profiles').find('userid', userid)[0]
            statistics = list(mongodbclient('instagram', 'statistics').find('userid', userid))

            followers = profile['followers']

            totalLikes = 0
            totalComments = 0
            totalVideos = 0
            totalViews = 0

            for post in posts:
                totalLikes += post['likeCount']
                totalComments += post['commentCount']
                totalVideos += 1 if post['isVideo'] else 0
                totalViews += post['videoViewCount']

            i = 0
            last = []
            while(i < last_posts and len(posts) > i):
                likes = posts[i]['likeCount']
                comments = posts[i]['commentCount']
                interactions = likes + comments
                date = posts[i]['date']
                last.append({
                    'likes': likes,
                    'comments': comments,
                    'date': date,
                    'engagement': (interactions / followers) * 100
                })
                i += 1

            interactions = totalLikes + totalComments
            return {
                'userid': userid,
                'likesCount': totalLikes,
                'commentsCount': totalComments,
                'lastPosts': last,
                'interactions': interactions,
                'statistics': statistics,
                'viewsCount': totalViews,
                'videosCount': totalVideos,
                'nextPost': self.prediction_post(posts) if len(posts) else {}
            }
        except Exception as e:
            print(e)
        return {}
    
    def get_comments(self, mediaid):
        result = []
        try:
            client = mongodbclient('instagram', 'comments')
            comments = list(client.find('mediaid', mediaid))    
            return comments
        except Exception as e:
            print(f"erro ao coletar comentários {mediaid}: {e}")
        return result