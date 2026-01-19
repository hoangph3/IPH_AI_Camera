from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://root:password@localhost:27017/?authSource=admin")
database_name = "api_test"

# Function to check the structure of the cam_list collection in MongoDB
def check_cam_list_structure():
    collection = client[database_name]["cam_list"]
    sample_document = collection.find_one()

    if sample_document:
        return sample_document.keys()
    else:
        return None


# Check the structure of cam_list
structure = check_cam_list_structure()

if structure:
    print("Structure of cam_list collection:")
    for key in structure:
        print(key)
else:
    print("The cam_list collection is empty or does not exist.")
