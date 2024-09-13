from flask import Blueprint, jsonify, request
from app.models.youtube_model import youtube_model

youtube_bp = Blueprint('youtube', __name__)

@youtube_bp.route('/getchannel', methods=['GET'])
def get_channel():
    channel_id = request.args.get('channelId')
    if not channel_id:
        return jsonify({"error": "channelId é obrigatório"}), 400

    youtube = youtube_model()
    channel = youtube.get_channel_info(channel_id)

    if not channel:
        return jsonify({})
    
    if '_id' in channel:
        channel.pop('_id')

    return jsonify(channel)

@youtube_bp.route('/getvideos', methods=['GET'])
def get_videos():
    channel_id = request.args.get('channelId')
    if not channel_id:
        return jsonify({})
    
    youtube = youtube_model()
    videos = youtube.get_videos(channel_id)
    videos = [{k: v for k, v in video.items() if k != '_id'} for video in videos]
    return jsonify(videos)

@youtube_bp.route('getcomments', methods=['GET'])
def get_comments():
    video_id = request.args.get('videoId')
    if not video_id:
        return jsonify({})
    
    youtube = youtube_model()
    comments = youtube.get_comments(video_id)
    return jsonify(comments)


@youtube_bp.route('getplaylists', methods=['GET'])
def get_playlists():
    channel_id = request.args.get('channelId')
    if not channel_id:
        return jsonify([])
    try:
        youtube = youtube_model()
        playlists = youtube.get_playlists(channel_id)
        return list(map(lambda x: {
            'videosId': x['videosId'],
            'title': x['title']
        }, playlists))
    except:
        return jsonify([])
