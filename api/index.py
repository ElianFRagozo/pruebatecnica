from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
import traceback

# Initialize FastAPI app
app = FastAPI(title="User API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GET endpoint that returns a message and current date/time
@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido a la API de usuarios",
        "fecha_hora": datetime.now().isoformat()
    }

# Test endpoint that returns MongoDB connection status
@app.get("/test-db")
async def test_db():
    try:
        # Get MongoDB URI from environment variable
        mongodb_uri = os.getenv("MONGODB_URI")
        
        # Return error if URI is not set
        if not mongodb_uri:
            return {"status": "error", "message": "MONGODB_URI environment variable is not set"}
        
        # Create a client
        client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Test the connection
        await client.admin.command('ping')
        
        # Get database and collection info
        db_names = await client.list_database_names()
        
        # Close the connection
        client.close()
        
        return {
            "status": "success",
            "message": "Successfully connected to MongoDB",
            "databases": db_names
        }
    except Exception as e:
        error_details = traceback.format_exc()
        return {
            "status": "error",
            "message": str(e),
            "details": error_details,
            "mongodb_uri_exists": bool(os.getenv("MONGODB_URI"))
        }

# Simplified users endpoint
@app.get("/users-test")
async def get_users_test():
    try:
        # Get MongoDB URI from environment variable
        mongodb_uri = os.getenv("MONGODB_URI")
        
        # Create a client
        client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Get database and collection
        db = client.get_database('user_database')
        collection = db.get_collection('users')
        
        # Count documents
        count = await collection.count_documents({})
        
        # Close the connection
        client.close()
        
        return {
            "status": "success",
            "message": f"Found {count} users in the database"
        }
    except Exception as e:
        error_details = traceback.format_exc()
        return {
            "status": "error",
            "message": str(e),
            "details": error_details
        }

app = app

