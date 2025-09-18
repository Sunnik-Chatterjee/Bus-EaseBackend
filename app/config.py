from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB Atlas connection string from environment
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "bus_ease"

try:
    # Connect to MongoDB Atlas
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Test the connection
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
except Exception as e:
    print(f"❌ Error connecting to MongoDB Atlas: {e}")
    client = None
    db = None
