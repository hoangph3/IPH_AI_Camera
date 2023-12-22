import pymongo

from . import GenericBackend
from .exceptions import ObjectIdExists, ObjectIdNotFound


class MongoBackend(GenericBackend):
    def __init__(self, uri=None):
        super().__init__(uri)

    def connect(self, config):
        self.client = pymongo.MongoClient(config)

    def get_collection(self, db_name, collection_name):
        db = self.client[db_name]
        collection = db[collection_name]
        return collection

    def drop_collection(self, db_name, collection_name):
        collection = self.get_collection(db_name, collection_name)
        collection.drop()

    def get(self, db_name, collection_name, _filter=None, as_list=False):
        if not isinstance(_filter, dict):
            _filter = {}
        collection = self.get_collection(db_name, collection_name)
        records = collection.find(_filter)
        if as_list is True:
            return list(records)

        return records

    def create(self, db_name, collection_name, data):
        collection = self.get_collection(db_name, collection_name)

        if isinstance(data, list):
            result = collection.insert_many(data)
            return list(map(str, result.inserted_ids))

        _id = data.get('_id')
        if self.get(db_name, collection_name, _ids=_id):
            raise ObjectIdExists(collection_name, _id)

        result = collection.insert_one(data)
        return str(result.inserted_id)

    def update(self, db_name, collection_name, data):
        collection = self.get_collection(db_name, collection_name)
        collection.update_one({
            "_id": data["_id"],
            "$set": data
        })
        return str(data['_id'])

    def delete(self, db_name, collection_name, data):
        collection = self.get_collection(db_name, collection_name)
        if "_id" not in data:
            raise ObjectIdNotFound(collection_name, None)

        result = collection.delete_one({"_id": data["_id"]})
        if not result:
            raise ObjectIdNotFound(collection_name, data["_id"])

        return str(data["_id"])
