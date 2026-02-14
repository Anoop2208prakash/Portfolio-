import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Connect using the URI from your .env file
client = MongoClient(os.getenv("MONGO_URI"))
db = client.my_portfolio_db
projects_collection = db.projects