import pymongo

def clear_mongodb():
    """Clear all stored values from MongoDB"""
    try:
        # Connect to MongoDB
        mongo_client = pymongo.MongoClient('mongodb://localhost:27017/SIGN')
        mongo_db = mongo_client['SIGN']
        mongo_collection = mongo_db['sentences']
        
        # Get count before deletion
        count_before = mongo_collection.count_documents({})
        
        # Delete all documents
        result = mongo_collection.delete_many({})
        
        # Get count after deletion
        count_after = mongo_collection.count_documents({})
        
        print(f"✅ MongoDB cleared successfully!")
        print(f"📊 Documents deleted: {result.deleted_count}")
        print(f"📊 Documents before: {count_before}")
        print(f"📊 Documents after: {count_after}")
        
        # Close connection
        mongo_client.close()
        
    except Exception as e:
        print(f"❌ Error clearing MongoDB: {e}")

if __name__ == "__main__":
    print("🗑️ Clearing all stored values from MongoDB...")
    clear_mongodb()
    print("✅ Done!") 