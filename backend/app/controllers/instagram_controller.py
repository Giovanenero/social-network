from flask import Blueprint, Response, jsonify, request
from app.models.instagram_model import instagram_model
from app.models.mongodbclient import mongodbclient

instagram_bp = Blueprint('instagram', __name__)

@instagram_bp.route('/getprofiles', methods=['GET'])
def get_profiles():
    try:
        profiles = instagram_model().get_profiles()
        return jsonify(profiles), 200
    except Exception as e:
        return jsonify([]), 400

@instagram_bp.route('/image/<file_id>', methods=['GET'])
def get_image(file_id):
    try:
        client = mongodbclient('instagram')
        file = client.get_image_gridFS(file_id)
        if file:
            return Response(file.read(), mimetype='image/jpeg')
    except:
        return jsonify({}), 400

@instagram_bp.route('/getposts', methods=['GET'])
def get_posts():
    try:
        userid = request.args.get('userid')
        skip = int(request.args.get('skip'))
        limit = int(request.args.get('limit'))
        posts = instagram_model().get_posts(userid, skip, limit)
        posts = list(posts)
        return jsonify(posts)
    except:
        return jsonify([]), 400
    
@instagram_bp.route('/getmetrics', methods=['GET'])
def get_metrics():
    try:
        user_id = request.args.get('userid')
        metrics = instagram_model().get_metrics(user_id)
        return jsonify(metrics), 200
    except:
        return jsonify({}), 400
    
@instagram_bp.route('/getcomments', methods=['GET'])
def get_comments():
    try:
        mediaid = request.args.get('mediaid')
        comments = instagram_model().get_comments(mediaid)
        comments = list(comments)

        return jsonify(comments), 200
    except:
        return jsonify({}), 400