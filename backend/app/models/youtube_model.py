from googleapiclient.discovery import build
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class youtube_model:
    def __init__(self, api_key):
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def get_channel_info(self, channel_id):
        try:
            res = self.youtube.channels().list(
                part="snippet", 
                id=channel_id
            ).execute()
            channel = res.get("items", [])
            channel = channel[0]

            # extração dos dados
            channel_info = {
                "channelId": channel_id,
                "title": channel.get("snippet", {}).get("title", ""),
                "description": channel.get("snippet", {}).get("description", ""),
                "publishedAt": channel.get("snippet", {}).get("publishedAt", ""),
                "imgUrl": channel.get("snippet", {}).get("thumbnails",{}).get("high", {}).get("url", ""),
                "country": channel.get("snippet", {}).get("country", ""),
                "customUrl": channel.get("snippet", {}).get("customUrl", ""),
            }

            # coleta dados estatísticos do canal
            res = self.youtube.channels().list(
                part="statistics", 
                id=channel_id
            ).execute()
            channel = res.get("items", [])
            channel = channel[0]

            channel_info.update({
                "viewCount": channel.get("statistics", {}).get("viewCount", 0),
                "subscriberCount": channel.get("statistics", {}).get("subscriberCount", 0),
                "videoCount": channel.get("statistics", {}).get("videoCount", 0),
                "extraction": str(datetime.now()),
            })

            ##adiciona ou atualiza as informações no mongodb
            #client = mongodbclient('youtube', 'channels')
            #if len(client.find('channelId', channel_id)) > 0:
            #    client.update('channelId', channel_id, channel_info)
            #else:
            #    client.insert(channel_info)


            return channel_info
        except Exception as e:
            logging.error("Erro ao coletar canal: %s", e)

        return {}
    
    # dado um id do canal, retorna todos as playlists do canal
    def get_playlists(self, channel_id):
        try:
            playlists = []
            next_page_token = None
            
            # Coletar todos os comentários principais
            while True:
                res = self.youtube.playlists().list(
                    part="snippet",
                    channelId=channel_id,
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
                    logging.error("Erro ao coletar items do canal: %s", e)
            return data
        except Exception as e:
            logging.error("Erro ao coletar vídeos: %s", e)
        return []

    def get_video_statistics(self, video_id):
        video_info = {
            "viewCount": 0,
            "likeCount": 0,
            "dislikeCount": 0,
            "favoriteCount": 0,
            "commentCount": 0
        }
        try:
            res = self.youtube.videos().list(part="statistics", id=video_id).execute()
            statistics = res.get("items", [])
            statistics = statistics[0]
            if statistics:
                video_info = {
                    "viewCount": statistics.get("statistics", {}).get("viewCount", 0),
                    "likeCount": statistics.get("statistics", {}).get("likeCount", 0),
                    "dislikeCount": statistics.get("statistics", {}).get("dislikeCount", 0),
                    "favoriteCount": statistics.get("statistics", {}).get("favoriteCount", 0),
                    "commentCount": statistics.get("statistics", {}).get("commentCount", 0)
                }
        except Exception as e:
            logging.error("Erro ao coletar estatísticas do vídeo %s: %s", video_id, e)
        return video_info

    def get_video_content_details(self, video_id):
        try:
            res = self.youtube.videos().list(part="contentDetails", id=video_id, maxResults=50).execute()
            contentDetails = res.get("items", [])
            contentDetails = contentDetails[0]
            if contentDetails:
                return {"duration": contentDetails.get("contentDetails", {}).get("duration", "")}
        except Exception as e:
            logging.error(f"Erro ao coletar a duração do vídeo {video_id}: {e}")
        return {"duration": ""}


    # dado um id do vídeo, carrega todos os comentários e respostas
    def get_comments(self, video_id):
        try:
            comments = []
            next_page_token = None
            
            # Coletar todos os comentários principais
            while True:
                res = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page_token
                ).execute()
                comments.extend(res.get("items", []))
                next_page_token = res.get("nextPageToken")
                if not next_page_token:
                    break
            
            all_comments_data = []
            
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
                
                # Coletar respostas para o comentário principal
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
                all_comments_data.append(comment_data)

            # adiciona ou atualiza os comentários do video no mongodb
            #TODO: fazer uma rotina e não isso aqui
            #client = mongodbclient('youtube', "comments")
            #for comment in all_comments_data:
            #    if len(client.find('commentId', comment['commentId'])) > 0:
            #        client.update('commentId', comment['commentId'], comment)
            #    else:
            #        client.insert(comment)
            
            return all_comments_data
        
        except Exception as e:
            print(f"Erro ao coletar comentários: {e}")
            return []
        

    def get_videos(self, channel_id):

        # coleta a playlist padrão do youtube que contém todos os vídeos de um usuário
        response = self.youtube.channels().list(
            part='contentDetails',
            id=channel_id
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

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        videosId = list(map(lambda x: x["snippet"]["resourceId"]["videoId"], videos))

        # pega todos os vídeos do usuário
        try:
            next_page_token = None
            videos = []
            while True:
                res = self.youtube.videos().list(
                    part="snippet",
                    id=videosId,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                videos += res.get("items", [])
                next_page_token = res.get("nextPageToken")
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

            # adiciona ou atualiza os videos no mongodb
            #TODO: fazer uma rotina e não isso aqui
            #client = mongodbclient('youtube', "videos")
            #for video in videos_info:
            #    if len(client.find('videoId', video['videoId'])) > 0:
            #        client.update('videoId', video['videoId'], video)
            #    else:
            #        client.insert(video)

            return videos_info
        except Exception as e:
            print(f"Erro ao coletar vídeos: {e}")
            return []