from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
import os
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# MongoDB connection function
async def get_mongodb_client():
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise HTTPException(status_code=500, detail="MONGODB_URI environment variable is not set")
    
    client = AsyncIOMotorClient(
        mongodb_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    
    # Test the connection
    try:
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# User model
class User(BaseModel):
    nombre: str
    email: EmailStr

class UserInDB(User):
    id: Optional[str] = None

# GET endpoint that returns a message and current date/time
@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido a la API de usuarios",
        "fecha_hora": datetime.now().isoformat()
    }

# POST endpoint to add a new user
@app.post("/users", response_model=UserInDB)
async def create_user(user: User):
    try:
        logger.info(f"Attempting to create user with email: {user.email}")
        
        # Get MongoDB client
        client = await get_mongodb_client()
        
        # Get database and collection
        db = client.get_database('user_database')
        collection = db.get_collection('users')
        
        # Check if user exists
        existing_user = await collection.find_one({"email": user.email})
        if existing_user:
            logger.warning(f"User with email {user.email} already exists")
            client.close()
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Insert user
        user_dict = user.dict()
        result = await collection.insert_one(user_dict)
        logger.info(f"Successfully created user with ID: {result.inserted_id}")
        
        # Get created user
        created_user = await collection.find_one({"_id": result.inserted_id})
        
        # Close the connection
        client.close()
        
        return {
            "id": str(created_user["_id"]),
            "nombre": created_user["nombre"],
            "email": created_user["email"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

# GET endpoint to retrieve all users
@app.get("/users")
async def get_users():
    try:
        logger.info("Attempting to retrieve all users")
        
        # Get MongoDB client
        client = await get_mongodb_client()
        
        # Get database and collection
        db = client.get_database('user_database')
        collection = db.get_collection('users')
        
        # Find all users
        users = []
        async for user in collection.find():
            users.append({
                "id": str(user["_id"]),
                "nombre": user["nombre"],
                "email": user["email"]
            })
        
        # Close the connection
        client.close()
        
        logger.info(f"Successfully retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving users: {str(e)}"
        )

# Test endpoint that returns MongoDB connection status (keep this for debugging)
@app.get("/test-db")
async def test_db():
    try:
        client = await get_mongodb_client()
        db_names = await client.list_database_names()
        client.close()
        
        return {
            "status": "success",
            "message": "Successfully connected to MongoDB",
            "databases": db_names
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

app = app

