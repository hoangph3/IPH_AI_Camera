from pymongo import ASCENDING, MongoClient
from loguru import logger

# Connect to MongoDB
client = MongoClient(
    "mongodb://root:password@localhost:27017/?authSource=admin")

while True:
    db = client['reid']
    
