import os
from googleapiclient.discovery import build
from datetime import datetime
import logging

from pymongo import MongoClient
from telegram import Update

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
API_KEY = os.getenv("API_KEY_YOUTUBE_DATA")
MONGO_URI = os.getenv("MONGO_URI")

class YouTube:
    def __init__(self, update: Update):
        self.youtube = build("youtube", "v3", developerKey=API_KEY)
        self.channel_id = 'UCaldTW0ntt8_XOvllDpI0Dw'
        self.update = update
        self.client = MongoClient(MONGO_URI)
        self.db = self.client['youtube']
        self.collection_channels = self.db['channels']
        self.collection_videos = self.db['videos']
        self.collection_comments = self.db['comments']
        self.collection_playlists = self.db['playlists']
        #self.collection_statistics = self.db['statistics']

        self.collection_channels.create_index('channelId', unique=True)
        self.collection_videos.create_index('videoId', unique=True)
        self.collection_comments.create_index('commentId', unique=True)
        self.collection_playlists.create_index('playlistId', unique=True)

    def extract_channel(self):
        try:
            res = self.youtube.channels().list(
                part="snippet,statistics",
                id=self.channel_id
            ).execute()
            channel = res.get("items", [])[0]
            
            channel_info = {
                "channelId": self.channel_id,
                "title": channel.get("snippet", {}).get("title", ""),
                "description": channel.get("snippet", {}).get("description", ""),
                "publishedAt": channel.get("snippet", {}).get("publishedAt", ""),
                "imgUrl": channel.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url", ""),
                "country": channel.get("snippet", {}).get("country", ""),
                "customUrl": channel.get("snippet", {}).get("customUrl", ""),
                "viewCount": channel.get("statistics", {}).get("viewCount", 0),
                "subscriberCount": channel.get("statistics", {}).get("subscriberCount", 0),
                "videoCount": channel.get("statistics", {}).get("videoCount", 0),
                "extraction": str(datetime.now())
            }

            self.collection_channels.update_one(
                {'channelId': channel_info['channelId']},
                {"$set": channel_info},
                upsert=True
            )

        except Exception as e:
            logging.error("Erro ao coletar canal: %s", e)

    def extract_playlists(self):
        try:
            playlists = []
            next_page_token = None

            while True:
                res = self.youtube.playlists().list(
                    part="snippet",
                    channelId=self.channel_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                playlists.extend(res.get("items", []))
                next_page_token = res.get("nextPageToken")
                if not next_page_token:
                    break

            data = []
            for playlist in playlists:
                snippet = playlist.get("snippet", {})
                playlist_data = {
                    "playlistId": playlist["id"],
                    "channelId": snippet.get("channelId", ""),
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "imgUrl": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "extraction": str(datetime.now()),
                    "videosId": []
                }
                try:
                    videos = []
                    next_page_token = None
                    while True:
                        res = self.youtube.playlistItems().list(
                            part="snippet",
                            playlistId=playlist["id"],
                            maxResults=50,
                            pageToken=next_page_token
                        ).execute()
                        videos.extend(res.get("items", []))
                        next_page_token = res.get("nextPageToken")
                        if not next_page_token:
                            break

                    playlist_data["videosId"] = list(map(lambda x: x["snippet"]["resourceId"]["videoId"], videos))
                    data.append(playlist_data)

                except Exception as e:
                    logging.error("Erro ao coletar items do playlist: %s", e)

                for playlist in data:
                    self.collection_playlists.update_one(
                        {'playlistId': playlist['playlistId']},
                        {"$set": playlist},
                        upsert=True
                    )
        except Exception as e:
            logging.error("Erro ao coletar playlists: %s", e)

    def get_video_statistics(self, video_id):
        try:
            res = self.youtube.videos().list(part="statistics", id=video_id).execute()
            statistics = res.get("items", [])[0].get("statistics", {})
            return {
                "viewCount": statistics.get("viewCount", 0),
                "likeCount": statistics.get("likeCount", 0),
                "dislikeCount": statistics.get("dislikeCount", 0),
                "favoriteCount": statistics.get("favoriteCount", 0),
                "commentCount": statistics.get("commentCount", 0)
            }
        except Exception as e:
            logging.error("Erro ao coletar estatísticas do vídeo %s: %s", video_id, e)
        return {}

    def get_video_content_details(self, video_id):
        try:
            res = self.youtube.videos().list(part="contentDetails", id=video_id).execute()
            content_details = res.get("items", [])[0].get("contentDetails", {})
            return {"duration": content_details.get("duration", "")}
        except Exception as e:
            logging.error("Erro ao coletar a duração do vídeo %s: %s", video_id, e)
        return {"duration": ""}

    def extract_videos(self):
        try:
            response = self.youtube.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()

            if 'items' not in response or len(response['items']) == 0:
                return []
            
            playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            videos = []
            next_page_token = None
            while True:
                res = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                videos.extend(res['items'])

                next_page_token = res.get('nextPageToken')
                if not next_page_token:
                    break

            videos_id = list(map(lambda x: x["snippet"]["resourceId"]["videoId"], videos))

            videos = []
            while True:
                res = self.youtube.videos().list(
                    part="snippet",
                    id=','.join(videos_id),
                    maxResults=50
                ).execute()
                videos.extend(res.get("items", []))

                next_page_token = res.get('nextPageToken')
                if not next_page_token:
                    break

            videos_info = []
            for video in videos:
                snippet = video.get("snippet", {})
                video_info = {
                    "videoId": video.get("id", ""),
                    "channelId": snippet.get("channelId", ""),
                    "description": snippet.get("description", ""),
                    "title": snippet.get("title", ""),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "imgUrl": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "tags": snippet.get("tags", [])
                }
                video_info.update(self.get_video_statistics(video_info["videoId"]))
                video_info.update(self.get_video_content_details(video_info["videoId"]))
                video_info["extraction"] = str(datetime.now())
                videos_info.append(video_info)

            for video in videos_info:
                self.collection_videos.update_one(
                    {'videoId': video['videoId']},
                    {"$set": video},
                    upsert=True
                )
        except Exception as e:
            logging.error("Erro ao coletar vídeos: %s", e)
        return []
    
    def extract_comments(self):
        
        videos = self.collection_comments.find(
            {'channelId': self.channel_id, 'commentCount': {'$gt': 0}}
        )

        for video in videos:
            try:
                comments = []
                next_page_token = None

                while True:
                    res = self.youtube.commentThreads().list(
                        part="snippet",
                        videoId=video['videoId'],
                        maxResults=100,
                        pageToken=next_page_token
                    ).execute()
                    comments.extend(res.get("items", []))
                    next_page_token = res.get("nextPageToken")
                    if not next_page_token:
                        break

                for comment_thread in comments:
                    snippet = comment_thread.get("snippet", {})
                    top_level_comment = snippet.get("topLevelComment", {}).get("snippet", {})

                    comment_data = {
                        "commentId": comment_thread.get("id", ""),
                        "videoId": snippet.get("videoId", ""),
                        "channelId": snippet.get("channelId", ""),
                        "textOriginal": top_level_comment.get("textOriginal", ""),
                        "authorProfileImageUrl": top_level_comment.get("authorProfileImageUrl", ""),
                        "likeCount": top_level_comment.get("likeCount", 0),
                        "dislikeCount": top_level_comment.get("dislikeCount", 0),
                        "publishedAt": top_level_comment.get("publishedAt", ""),
                        "authorDisplayName": top_level_comment.get("authorDisplayName", ""),
                        "replies": []
                    }

                    replies = snippet.get("totalReplyCount", 0)
                    if replies > 0:
                        next_page_token_replies = None
                        while True:
                            res_replies = self.youtube.comments().list(
                                part="snippet",
                                parentId=comment_thread.get("id", ""),
                                maxResults=100,
                                pageToken=next_page_token_replies
                            ).execute()

                            for reply in res_replies.get("items", []):
                                reply_snippet = reply.get("snippet", {})
                                comment_data["replies"].append({
                                    "commentId": reply.get("id", ""),
                                    "videoId": snippet.get("videoId", ""),
                                    "channelId": reply_snippet.get("authorChannelId", {}).get("value", ""),
                                    "textOriginal": reply_snippet.get("textOriginal", ""),
                                    "authorProfileImageUrl": reply_snippet.get("authorProfileImageUrl", ""),
                                    "likeCount": reply_snippet.get("likeCount", 0),
                                    "dislikeCount": reply_snippet.get("dislikeCount", 0),
                                    "publishedAt": reply_snippet.get("publishedAt", ""),
                                    "authorDisplayName": reply_snippet.get("authorDisplayName", ""),
                                    "extraction": str(datetime.now())
                                })

                            next_page_token_replies = res_replies.get("nextPageToken")
                            if not next_page_token_replies:
                                break

                    comment_data["extraction"] = str(datetime.now())

                    self.collection_comments.update_one(
                        {'commentId': comment_data['commentId']},
                        {"$set": comment_data},
                        upsert=True
                    )
            except Exception as e:
                logging.error("Erro ao coletar comentários: %s", e)
