from pymongo import MongoClient
from faker import Faker

# Replace these values with your MongoDB credentials and connection details
username = "root"
password = "password"
host = "localhost"
port = 27017

# Connect to MongoDB with authentication
client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/")
db = client["api_test"]
cam_list_collection = db["cam_list"]

# Generate fake RTSP camera entries using Faker
fake = Faker()
cameras = [
    {"name": "cam6", "rtsp_url": f"rtsp://admin:kotora2023@192.168.1.168:554/ch01/2"}
]

# Insert fake RTSP camera entries into the cam_list collection
cam_list_collection.insert_many(cameras)

print("Fake RTSP camera entries inserted successfully.")
