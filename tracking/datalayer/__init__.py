from abc import abstractmethod


class GenericBackend(object):
    def __init__(self, uri=None):
        self.uri = uri
        self.client = None
        self.connect(self.uri)

    @abstractmethod
    def connect(self, config):
        pass

    @abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        pass
