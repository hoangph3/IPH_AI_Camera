from datalayer.mongo import MongoBackend


class Database:
    def __init__(self, config):
        self.config = config
        self.mongo_tracking = MongoBackend(uri=config.backend.mongo.tracking.uri)
        self.mongo_reid = MongoBackend(uri=config.backend.mongo.reid.uri)
        self.mongo_report = MongoBackend(uri=config.backend.mongo.report.uri)

    def get_history_tracking_data(self, time_from=None, time_to=None):
        _filter = {'timestamp': {}}
        if time_from is not None:
            _filter['timestamp']["$gte"] = time_from
        if time_to is not None:
            _filter['timestamp']["$lte"] = time_to

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
            [('timestamp', -1)]
        ).limit(
            1
        )

        records = list(records)
        if not len(records):
            return {}

        return records[0]

    def get_history_reid_data(self, time_from=None, time_to=None):
        _filter = {'query_time': {}}
        if time_from is not None:
            _filter['query_time']["$gte"] = time_from
        if time_to is not None:
            _filter['query_time']["$lte"] = time_to

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
            [('query_time', -1)]
        ).limit(
            1
        )

        records = list(records)
        if not len(records):
            return {}

        return records[0]

    def get_last_report_data(self):
        records = self.mongo_report.get(
            db_name=self.config.backend.mongo.report.database,
            collection_name=self.config.backend.mongo.report.collection,
            _filter=None
        ).sort(
            [('end_time', -1)]
        ).limit(
            1
        )

        records = list(records)
        if not len(records):
            return {}

        return records[0]

    def write_reid_data(self, data):
        self.mongo_reid.create(
            db_name=self.config.backend.mongo.reid.database,
            collection_name=self.config.backend.mongo.reid.collection,
            data=data
        )

    def write_report_data(self, data):
        self.mongo_report.create(
            db_name=self.config.backend.mongo.report.database,
            collection_name=self.config.backend.mongo.report.collection,
            data=data
        )
