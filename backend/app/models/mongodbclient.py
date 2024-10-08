import gridfs
from pymongo import MongoClient
import logging
from bson.objectid import ObjectId
import os

MONGO_URI = os.getenv("MONGO_URI")

class mongodbclient:
    def __init__(self, database, collection=None):
        self.client = MongoClient(MONGO_URI)
        self.database = self.client[database]
        if collection:
            self.collection = self.database[collection]
        else:
            self.collection = None

    def get_image_gridFS(self, file_id):
        try:
            fs = gridfs.GridFS(self.database)
            file = fs.get(ObjectId(file_id))
            if file:
                return file
        except Exception as e:
            print(f"erro ao coletar arquivo com id {file_id}: {e}")
        return ""

    def find(self, key, value, skip = 0, limit = None, fields=None, sort_name = None, ascending = True):
        try:
            query = {key: value}
            projection = fields if fields is not None else {'_id': 0}
            cursor = self.collection.find(query, projection).skip(skip)
            if sort_name is not None:
                order = 1 if ascending else -1
                cursor.sort(sort_name, order)
            if limit is not None:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logging.error("Error finding data: %s", e, exc_info=True)
            return []

    def insert(self, data, many = False):
        try:
            if many:
                self.collection.insert_many(data)
            else:
                self.collection.insert_one(data)
        except Exception as e:
            logging.error("Error inserting data: %s", e)

    def sort(self, field, ascending=True):
        try:
            direction = 1 if ascending else -1
            return list(self.collection.find().sort(field, direction))
        except Exception as e:
            logging.error("Error sorting data: %s", e)
        return []

    def delete(self, key, value, many=False):
        query = {key: value}
        try:
            if many:
                self.collection.delete_many(query)
            else:
                self.collection.delete_one(query)
        except Exception as e:
            logging.error("Error deleting data: %s", e)

    def update(self, key, value, update_data, many=False):
        query = {key: value}
        update_data = {"$set": update_data}
        try:
            if many:
                self.collection.update_many(query, update_data)
            else:
                self.collection.update_one(query, update_data)
        except Exception as e:
            logging.error("Error updating data: %s", e)
