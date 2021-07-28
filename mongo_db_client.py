import ssl

import pymongo
from pymongo import MongoClient


class MongoDBClient:

    client: MongoClient

    def __init__(self):
        global client
        client = pymongo.MongoClient(
            "mongodb+srv://bdat2020:bdat2020@cluster0.pukvu.mongodb.net/Mobile_Details?retryWrites=true&w=majority",
            ssl_cert_reqs=ssl.CERT_NONE)

    def upload_reviews(self, review):
        global client
        # Get reference to the tables
        db = client.app_reviews
        # Get reference to news table from db
        collection = db["app_reviews"]

        # Iterate the list and insert news one by one
        collection.insert_one(review)

    def upload_tag(self, tag):
        global client
        # Get reference to the tables
        db = client.app_reviews
        # Get reference to news table from db
        collection = db["app_tags"]
        # Iterate the list and insert news one by one
        collection.insert_one(tag)