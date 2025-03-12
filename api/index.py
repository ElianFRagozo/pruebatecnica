from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
import os
from typing import Optional

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

# MongoDB connection with better handling for serverless
MONGODB_URL = os.getenv("MONGODB_URI")
client = None
db = None
user_collection = None

async def get_database():
    global client, db, user_collection
    if client is None:
        try:
            client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
            # Ping the server to confirm connection
            await client.admin.command('ping')
            print("Connected successfully to MongoDB!")
            db = client.user_database
            user_collection = db.users
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
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
        collection = await get_database()
        
        # Check if user with this email already exists
        if await collection.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Insert user into database
        user_dict = user.dict()
        result = await collection.insert_one(user_dict)
        
        # Return created user with ID
        created_user = await collection.find_one({"_id": result.inserted_id})
        return {
            "id": str(created_user["_id"]),
            "nombre": created_user["nombre"],
            "email": created_user["email"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# GET endpoint to retrieve all users
@app.get("/users")
async def get_users():
    try:
        collection = await get_database()
        users = []
        async for user in collection.find():
            users.append({
                "id": str(user["_id"]),
                "nombre": user["nombre"],
                "email": user["email"]
            })
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

app = app

