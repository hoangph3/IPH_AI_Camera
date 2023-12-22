import chromadb
from chromadb.config import Settings


class ChromaBackend:
    def __init__(self, host="localhost", port=8000, metric=None):
        if metric is None:
            raise ValueError("Metric must be 'euclidean' or 'cosine'")
        self.client = chromadb.HttpClient(
            host=host, port=port, settings=Settings(anonymized_telemetry=False)
        )
        self.index_params = {'hnsw:space': metric}

    def create(self, collection):
        self.client.get_or_create_collection(
            name=collection, metadata=self.index_params
        )

    def drop(self, collection):
        return self.client.delete_collection(collection)

    def get(self, collection, filter={'global_id': {'$ne': ''}}):
        col = self.client.get_or_create_collection(collection, self.index_params)
        results = col.get(where=filter, include=['metadatas'])['metadatas']
        return results

    def insert(self, collection, embeddings, ids, metadatas):
        col = self.client.get_or_create_collection(collection, self.index_params)
        col.add(embeddings=embeddings, ids=ids, metadatas=metadatas)

    def search(self, collection, embeddings, topk):
        col = self.client.get_or_create_collection(collection, self.index_params)
        results = col.query(embeddings, n_results=topk)
        return results

    def delete(self, collection, ids):
        col = self.client.get_or_create_collection(collection, self.index_params)
        col.delete(ids=ids)
