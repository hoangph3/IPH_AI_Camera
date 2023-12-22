from sklearn.cluster import AgglomerativeClustering, DBSCAN
from loguru import logger
import numpy as np
import time

from utility.hparams import HParams
from utility.database import Database
from utility import handler
from datalayer.chroma import ChromaBackend


class Matching:
    def __init__(self, config: HParams) -> None:
        self.config = config
        self.database = Database(config=config)
        self.chroma_client = ChromaBackend(
            host=config.backend.chroma.host,
            port=config.backend.chroma.port,
            metric=config.metric
        )

    def get_centroids(self, X: np.ndarray):
        return np.mean(X, axis=0)

    def run(self):
        logger.info("Matching start.")

        while True:
            # Get last tracking data
            last_tracking_dt = self.database.get_last_tracking_data()
            last_tracking_time = last_tracking_dt.get(self.database.time_field)
            if last_tracking_time is None:
                time.sleep(self.config.interval)
                continue

            # Continue to collect more data
            if handler.get_time() - last_tracking_time < self.config.batch_time:
                time.sleep(self.config.interval)    
                continue

            # Get history tracking data
            tracking_dt = self.database.get_history_tracking_data(
                time_from=last_tracking_time, time_to=handler.get_time()
            )
            embeddings = [doc['feature_embeddings'] for doc in tracking_dt]

            # Clustering
            clustering_params = {
                'n_clusters': None,
                'metric': self.config.metric,
                'distance_threshold': self.config.clustering.threshold,
                'linkage': self.config.clustering.linkage
            }
            clustering = AgglomerativeClustering(**clustering_params).fit(embeddings)

            # Get clusters
            labels = clustering.labels_
            num_clusters = clustering.n_clusters_
            logger.info("Clustering: {} clusters".format(num_clusters))

            # Get centroids
            centroids = []
            for cluster_idx in range(num_clusters):
                centroid = self.get_centroids(embeddings[labels == cluster_idx])
                centroids.append(centroid)

            # Search by centroids & unpack results
            batch_results = self.chroma_client.search(
                collection=self.config.backend.chroma.collection,
                embeddings=centroids, topk=self.config.top_k
            )
            batch_ids = batch_results['ids']
            batch_distances = batch_results['distances']
            batch_metadatas = batch_results['metadatas']

            # Filter neighbors by threshold
            neighbors = []
            for ids, dists, metadatas in zip(batch_ids, batch_distances, batch_metadatas):
                neighbors = [
                    (_id, dist, metadata) for _id, dist, metadata in zip(
                        ids, dists, metadatas
                    ) if dist <= self.config.matching.threshold
                ]

            # Re-ID
            if len(neighbors) == 0:
                global_id = uuid4().hex
                # Insert vector db
                self.db.insert(
                    self.chroma_opts['db'],
                    embeddings=[embedding],
                    ids=[uuid4().hex],
                    metadatas=[{'global_id': global_id}]
                )

            else:
                # Get neighbor by min dist
                min_dist = neighbors[0][1]
                global_id = neighbors[0][2]['global_id']
                logger.info("Distance: {}, Exist id: {}".format(min_dist, global_id))

                