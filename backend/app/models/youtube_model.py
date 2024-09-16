from app.models.mongodbclient import mongodbclient

class youtube_model:

    def get_channel_info(self, channel_id):
        client = mongodbclient('youtube', 'channels')
        return client.find('channelId', channel_id)[0]
    
    def get_playlists(self, channel_id):
        client = mongodbclient('youtube', 'playlists')
        return client.find('channelId', channel_id)

    def get_comments(self, video_id):
        client = mongodbclient('youtube', 'comments')
        return client.find('videoId', video_id, sort_name="date", ascending=False)
        
    def get_videos(self, channel_id):
        client = mongodbclient('youtube', 'videos')
        return client.find('channelId', channel_id, sort_name="date", ascending=False)