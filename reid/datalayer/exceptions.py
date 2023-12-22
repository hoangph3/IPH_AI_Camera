class ObjectIdExists(Exception):
    def __init__(self, collection, _id):
        self.collection = collection
        self._id = _id

    def __str__(self):
        return (
            f"Object with id {self._id} is exists "
            f"in the collection {self.collection}"
        )


class ObjectIdNotFound(Exception):
    def __init__(self, collection, _id):
        self.collection = collection
        self._id = _id

    def __str__(self):
        return (
            f"Object with id {self._id} not found "
            f"in the collection {self.collection}"
        )
