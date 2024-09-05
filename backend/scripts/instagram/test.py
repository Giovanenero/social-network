from datetime import datetime
import time
import random
import instaloader
import requests
import os
from pymongo import MongoClient
import gridfs
from dotenv import load_dotenv

# Conectar ao MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['instagram']
collection_posts = db['posts']
fs = gridfs.GridFS(db)

query = {'mediaid': '3444843403580726425', 'userid': {'$ne': '5532940513'}}
count = collection_posts.count_documents(query) > 0
print(count)
if count:
    collection_posts.update_many(query, {"$set": {"medias": []}})
    print("atualizou...")