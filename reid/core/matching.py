from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import cdist
from collections import defaultdict
from loguru import logger
import numpy as np
import pandas as pd
import time

from utility.hparams import HParams
from utility.database import Database
from utility import handler
from datalayer.chroma import ChromaBackend
from .re_ranking import re_ranking


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

    def voting(self):
        pass

    def get_matching_neighbors(self, q_nbrs_dists, q_nbrs_metas, q_nbrs_embeds):
        match_q_nbrs_dists = []
        match_q_nbrs_metas = []
        match_q_nbrs_embeds = []
        for q_dists, q_metas, q_embeds in zip(q_nbrs_dists, q_nbrs_metas, q_nbrs_embeds):
            for q_dist, q_meta, q_embed in zip(q_dists, q_metas, q_embeds):
                # Remove outliers
                if q_dist > self.config.matching.threshold:
                    continue
                # Get candidates
                match_q_nbrs_dists.append(q_dist)
                match_q_nbrs_metas.append(q_meta)
                match_q_nbrs_embeds.append(q_embed)
        return match_q_nbrs_dists, match_q_nbrs_metas, match_q_nbrs_embeds

    def run(self, camera_graph: dict):
        logger.info("Matching start.")

        while True:
            # Get last tracking data
            last_tracking_dt = self.database.get_last_tracking_data()
            last_tracking_time = last_tracking_dt.get('timestamp')
            if last_tracking_time is None:
                time.sleep(self.config.interval)
                continue

            # Get last reid data
            last_reid_dt = self.database.get_last_reid_data()
            last_reid_time = last_reid_dt.get('query_time')
            if (last_reid_time is not None) and (
                (
                    handler.get_time() - last_reid_time < self.config.batch_time
                ) or (
                    last_tracking_time - last_reid_time  < self.config.batch_time
                )
            ):
                logger.info("Need more data, from last tracking: {}, last reid: {} to: {}".format(
                    handler.time2datetime(last_tracking_time),
                    handler.time2datetime(last_reid_time),
                    handler.time2datetime(handler.get_time())
                ))
                time.sleep(self.config.interval)
                continue

            # Get history tracking data
            tracking_dt = self.database.get_history_tracking_data(
                time_from=last_reid_time, time_to=handler.get_time()
            )
            logger.info("Tracking events: {}".format(len(tracking_dt)))

            features = np.array([doc['feature_embeddings'] for doc in tracking_dt])
            cam_ids = np.array([doc['camera_id'] for doc in tracking_dt])
            timestamps = np.array([doc['timestamp'] for doc in tracking_dt])
            box_images = np.array([doc['object_image'] for doc in tracking_dt])

            reid_events = []

            # TODO: Clustering
            clustering_params = {
                'n_clusters': None,
                'metric': self.config.metric,
                'distance_threshold': self.config.clustering.threshold,
                'linkage': self.config.clustering.linkage
            }
            clustering = AgglomerativeClustering(**clustering_params).fit(features)

            # Get clusters
            labels = clustering.labels_
            num_clusters = clustering.n_clusters_
            logger.info("Clustering: {} clusters".format(num_clusters))

            # TODO: Get queries
            for cluster_idx in range(num_clusters):
                # Arrange query by cluster id
                cluster_indices = labels == cluster_idx
                query = features[cluster_indices]
                cam_id = cam_ids[cluster_indices]
                timestamp = timestamps[cluster_indices]
                box_image = box_images[cluster_indices]

                # TODO: Search by query = (num_query, dim)
                search_query = self.chroma_client.search(
                    collection=self.config.backend.chroma.collection,
                    embeddings=query, topk=self.config.matching.top_k
                )  # (n_query, k)

                q_nbrs_dists = search_query['distances']
                q_nbrs_metas = search_query['distances']
                q_nbrs_embeds = search_query['distances']

                # Build candidates
                q_candidates = []

                for qidx in range(len(query)):
                    query_cam = cam_id[qidx]
                    neighbor_cam = camera_graph.get(query_cam)

                    q_dists = q_nbrs_dists[qidx]
                    q_metas = q_nbrs_metas[qidx]
                    q_embeds = q_nbrs_embeds[qidx]

                    for q_dist, q_meta, q_embed in zip(q_dists, q_metas, q_embeds):
                        # Remove outliers
                        if q_dist > self.config.matching.threshold:
                            continue
                        if neighbor_cam and q_meta["camera_id"] not in neighbor_cam:
                            continue

                        q_candidates.append({
                            'global_id': q_meta["global_id"],
                            'dist': q_dist
                        })

                # Candidates found
                if len(q_candidates):
                    df = pd.DataFrame(q_candidates)
                    stats = []
                    for global_id, sub_df in df.groupby('global_id'):
                        stats.append({
                            'global_id': global_id,
                            'dist': float(np.mean(sub_df['dist'].values.tolist()))
                        })
                    stats = sorted(stats, key=lambda d: d['dist'])
                    global_id = stats[0]['global_id']
                    dist = stats[0]['dist']
                else:
                    global_id = handler.get_id(short=True)
                    # Add new global_id
                    self.chroma_client.insert(
                        collection=self.config.backend.chroma.collection,
                        embeddings=query,
                        ids=[handler.get_id() for _ in range(len(query))],
                        metadatas=[{"global_id": global_id, "camera_id": cid} for cid in cam_id]
                    )
                    dist = -1

                # Reid events
                for qidx in range(len(query)):
                    event = {
                        "query_cam": cam_id[qidx],
                        "query_time": timestamp[qidx],
                        "global_id": global_id,
                        'dist': dist,
                        "box_img": box_image[qidx]
                    }
                    reid_events.append(event)

            # Write reid logs
            logger.info("Reid: {} events".format(len(reid_events)))
            self.database.write_reid_data(data=reid_events)

            # Wait to flush
            time.sleep(self.config.interval)
