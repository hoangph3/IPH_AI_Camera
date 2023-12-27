import pymongo
import pandas as pd
from IPython.display import display
import cv2
import os
import base64
import numpy as np


client = pymongo.MongoClient("mongodb://admin:password@localhost:27017/admin")  # Replace with your MongoDB connection string
db = client["iph"]  # Replace with your database name
collection = db["reid"]  # Replace with your collection name

result = list(collection.find({}))
df = pd.DataFrame(result)

display(df)
for user_id, cam_df in df.groupby('global_id'):
    user_dir = "../temp/{}".format(user_id)
    os.makedirs(user_dir, exist_ok=True)
    cam_docs = cam_df.to_dict('records')
    for doc in cam_docs:
        box_img = doc['box_img']
        img_data = base64.b64decode(box_img)
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite(os.path.join(user_dir, doc['query_cam']+".jpg"), image)
