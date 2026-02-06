"""
Quick script to test MongoDB connection.
Run: python test_mongo.py
"""
from pymongo import MongoClient

# Your connection string - update this
CONNECTION_STRING = "mongodb+srv://JayTech_456:%23Sunset123@agentic.prrlq6h.mongodb.net/?appName=Agentic"

try:
    print("Attempting to connect to MongoDB...")
    client = MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=5000)
    
    # Test connection with ping
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
    
    # List databases
    print("\nAvailable databases:")
    for db in client.list_database_names():
        print(f"  - {db}")
    
    client.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nCommon fixes:")
    print("1. Check username/password are correct")
    print("2. Make sure your IP is whitelisted in MongoDB Atlas")
    print("3. Check the cluster name is correct")
