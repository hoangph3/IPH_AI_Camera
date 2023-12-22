from datalayer.mongo import MongoBackend


class Database:
    def __init__(self, config):
        self.config = config
        self.mongo_tracking = MongoBackend(uri=config.backend.mongo.tracking.uri)
        self.mongo_reid = MongoBackend(uri=config.backend.mongo.reid.uri)
        self.time_field = 'timestamp'

    def get_history_tracking_data(self, time_from=None, time_to=None):
        _filter = {self.time_field: {}}
        if time_from is not None:
            _filter[self.time_field]["$gte"] = time_from
        if time_to is not None:
            _filter[self.time_field]["$lte"] = time_to

        records = self.mongo_tracking.get(
            db_name=self.config.backend.mongo.tracking.database,
            collection_name=self.config.backend.mongo.tracking.collection,
            _filter=_filter,
            as_list=True
        )
        return records

    def get_last_tracking_data(self):
        records = self.mongo_tracking.get(
            db_name=self.config.backend.mongo.tracking.database,
            collection_name=self.config.backend.mongo.tracking.collection,
            _filter=None
        ).sort(
            [(self.time_field, -1)]
        ).limit(
            1
        )

        records = list(records)
        if not len(records):
            return {}

        return records[0]

    def get_history_reid_data(self, time_from=None, time_to=None):
        _filter = {self.time_field: {}}
        if time_from is not None:
            _filter[self.time_field]["$gte"] = time_from
        if time_to is not None:
            _filter[self.time_field]["$lte"] = time_to

        records = self.mongo_reid.get(
            db_name=self.config.backend.mongo.reid.database,
            collection_name=self.config.backend.mongo.reid.collection,
            _filter=_filter,
            as_list=True
        )
        return records

    def get_last_reid_data(self):
        records = self.mongo_reid.get(
            db_name=self.config.backend.mongo.reid.database,
            collection_name=self.config.backend.mongo.reid.collection,
            _filter=None
        ).sort(
            [(self.time_field, -1)]
        ).limit(
            1
        )

        records = list(records)
        if not len(records):
            return {}

        return records[0]
