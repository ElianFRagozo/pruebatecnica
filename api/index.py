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

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URI")
client = None
db = None
user_collection = None

async def get_database():
    global client, db, user_collection
    if client is None:
        try:
            logger.info("Attempting to connect to MongoDB...")
            client = AsyncIOMotorClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            # Test the connection
            await client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
            # Initialize database and collection
            db = client.get_database('user_database')
            user_collection = db.get_collection('users')
            
            # Test collection access
            await user_collection.find_one({})
            logger.info("Successfully accessed users collection!")
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            if client:
                client.close()
                client = None
            raise HTTPException(
                status_code=500,
                detail=f"Could not connect to database: {str(e)}"
            )
    return user_collection

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
        collection = await get_database()
        
        # Check if user exists
        existing_user = await collection.find_one({"email": user.email})
        if existing_user:
            logger.warning(f"User with email {user.email} already exists")
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Insert user
        user_dict = user.dict()
        result = await collection.insert_one(user_dict)
        logger.info(f"Successfully created user with ID: {result.inserted_id}")
        
        # Get created user
        created_user = await collection.find_one({"_id": result.inserted_id})
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
        collection = await get_database()
        
        users = []
        async for user in collection.find():
            users.append({
                "id": str(user["_id"]),
                "nombre": user["nombre"],
                "email": user["email"]
            })
        
        logger.info(f"Successfully retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving users: {str(e)}"
        )

# Startup event to test database connection
@app.on_event("startup")
async def startup_db_client():
    try:
        await get_database()
    except Exception as e:
        logger.error(f"Failed to connect to database on startup: {str(e)}")

app = app

