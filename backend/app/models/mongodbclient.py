from pymongo import MongoClient
import logging

class mongodbclient:
    def __init__(self, database, collection):
        self.connection_string = "mongodb://localhost:27017"
        self.client = MongoClient(self.connection_string)
        self.database = self.client[database]
        self.collection = self.database[collection]

    def find(self, key, value):
        try:
            query = {key: value}
            data = []
            response = self.collection.find(query)
            for registry in response:
                data.append(registry)
            return data
        except Exception as e:
            logging.error("Error finding data: %s", e)
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
