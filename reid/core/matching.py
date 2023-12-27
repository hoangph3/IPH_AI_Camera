from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import cdist
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
                    last_reid_time - last_tracking_time < self.config.batch_time
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
                query = features[labels == cluster_idx]
                # Compute centroids
                centroid = self.get_centroids(query)

                # Get nearest neighbors of centroid
                nbrs = NearestNeighbors(
                    n_neighbors=min(self.config.clustering.n_neighbors, len(query)),
                    metric=self.config.metric
                ).fit(query)
                nearest_indices = nbrs.kneighbors([centroid], return_distance=False)
                query = query[nearest_indices.flatten()]
                cam_id = cam_ids[nearest_indices.flatten()]
                timestamp = timestamps[nearest_indices.flatten()]
                box_image = box_images[nearest_indices.flatten()]

                # TODO: Search by query = (num_query, dim)
                search_query = self.chroma_client.search(
                    collection=self.config.backend.chroma.collection,
                    embeddings=query, topk=self.config.matching.top_k
                )  # (n_query, k)

                q_nbrs_dists, q_nbrs_metas, q_nbrs_embeds = self.get_matching_neighbors(
                    q_nbrs_dists=search_query['distances'],
                    q_nbrs_metas=search_query['metadatas'],
                    q_nbrs_embeds=search_query['embeddings']
                )  # to be flattened to: (n_query x valid_k, )
                gallery = q_nbrs_embeds

                # Build candidates
                q_candidates = []

                ## Re-ranking
                if len(query) and len(gallery):
                    q_g_dist = cdist(query, gallery, self.config.metric)  # (n_query, n_query x valid_k, )
                    q_q_dist = cdist(query, query, self.config.metric)
                    g_g_dist = cdist(gallery, gallery, self.config.metric)
                    rerank_dist = re_ranking(
                        q_g_dist=q_g_dist, q_q_dist=q_q_dist, g_g_dist=g_g_dist,
                        k1=self.config.rerank.k1, k2=self.config.rerank.k2,
                        lambda_value=self.config.rerank.lambda_value
                    )  # (n_query, n_query x valid_k, )

                    for idx in range(len(query)):
                        # Get query info
                        query_cam = cam_id[idx]
                        query_time = timestamp[idx]
                        box_img = box_image[idx]

                        neighbor_cam = camera_graph.get(query_cam)

                        # Get matching indices
                        match_dist = q_g_dist[idx]
                        match_indices = np.where(match_dist <= self.config.matching.threshold)[0].tolist()
                        
                        # Get ranking indices
                        rank_dist = rerank_dist[idx]
                        rank_indices = np.where(rank_dist <= self.config.rerank.threshold)[0].tolist()

                        # Get intersection indices
                        candidate_indices = set(match_indices).intersection(set(rank_indices))

                        # Get candidates
                        for cidx in candidate_indices:
                            q_meta = q_nbrs_metas[cidx]
                            # continue if out scope of query camera
                            if neighbor_cam and (query_cam not in neighbor_cam):
                                continue

                            candidate = {
                                "query_cam": query_cam,
                                "query_time": int(query_time),
                                "global_id": q_meta["global_id"],
                                "cam_id": q_meta["camera_id"],
                                "dist": float(match_dist[cidx]),
                                "rerank_dist": float(rank_dist[cidx]),
                                "box_img": box_img
                            }
                            q_candidates.append(candidate)

                # TODO: Check neighbors is exists or not
                if not len(q_candidates):
                    # Generate new global_id
                    gid = handler.get_id(short=True)
                    ids = []
                    metadatas = []

                    # Create reid event
                    for idx in range(len(query)):
                        cid = cam_id[idx]
                        query_time = timestamp[idx]
                        box_img = box_image[idx]

                        ids.append(handler.get_id())
                        metadatas.append({"global_id": gid, "camera_id": cid})
                        reid_event = {
                            "query_cam": cid,
                            "query_time": int(query_time),
                            "global_id": gid,
                            "cam_id": cid,
                            "dist": -1,
                            "rerank_dist": -1,
                            "box_img": box_img
                        }
                        reid_events.append(reid_event)

                    # Insert new global_id
                    self.chroma_client.insert(
                        collection=self.config.backend.chroma.collection,
                        embeddings=query,
                        ids=ids,
                        metadatas=metadatas
                    )
                else:
                    q_df = pd.DataFrame(q_candidates)
                    # Sort by dist & rerank_dist
                    q_df = q_df.sort_values(by=['rerank_dist', 'dist'])
                    # Get top 1
                    reid_event = q_df.iloc[0].to_dict()
                    reid_events.append(reid_event)

            # Write reid logs
            logger.info("Reid: {} events".format(len(reid_events)))
            self.database.write_reid_data(data=reid_events)

            # Wait to flush
            time.sleep(self.config.interval)
