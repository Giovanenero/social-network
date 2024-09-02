from flask import Blueprint, Response, jsonify, request
from app.models.instagram_model import instagram_model
from app.models.mongodbclient import mongodbclient

instagram_bp = Blueprint('instagram', __name__)
usernames = ['wise.bifor', 'wise.archival', 'wise.thisplay', 'wise.sportskills', 'wise.cado', 'wise.systems']

@instagram_bp.route('/getprofiles', methods=['GET'])
def get_profiles():
    try:
        profiles = instagram_model().get_profiles()
        print(profiles)
        return jsonify(profiles), 200
    except Exception as e:
        return jsonify([]), 400

@instagram_bp.route('/image/<file_id>', methods=['GET'])
def get_image(file_id):
    print(file_id)
    try:
        client = mongodbclient('instagram')
        file = client.get_image_gridFS(file_id)
        if file:
            return Response(file.read(), mimetype='image/jpeg')
    except:
        return jsonify({}), 400

# @instagram_bp.route('/getposts', methods=['GET'])
# def get_posts():
#     try:
#         username = request.args.get('username')
#         start = request.args.get('start')
#         end = request.args.get('end')

#         if not username or not start or not end:
#             return jsonify([]), 400
#         elif end - start < 0 or end - start > 16:
#             return jsonify([]), 400
        
#         return jsonify(instagram_model().get_posts(username, start, end))
#     except:
#         return jsonify([]), 400
    
# @instagram_bp.route('/getcomments', methods=['GET'])
# def get_comments():
#     try:
#         shortcode = request.args.get('shortcode')
#         return jsonify(instagram_model.get_comments(shortcode))
#     except:
#         return jsonify({}), 400