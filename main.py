from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.sql import select
from databases import Database
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta


import os


USERNAME = os.getenv("username")
PASSWORD = os.getenv("password")
PSQLADDRESS = os.getenv("psqladdress")
PSQLDB = os.getenv("psqldb") # the db to use 







# Database configuration
DATABASE_URL = "postgresql://" + USERNAME + ":" + PASSWORD + "@" + PSQLADDRESS + "/" + PSQLDB

# SQLAlchemy engine, metadata, and table definition
engine = create_engine(DATABASE_URL)
metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("username", String, primary_key=True),
    Column("hashed_password", String),
)

# Database instance
database = Database(DATABASE_URL)

# FastAPI instance
app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Secret key and algorithm
SECRET_KEY = "your_secret_key"  # Replace with a secure random key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models
class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Create the users table if it doesn't exist
@app.on_event("startup")
async def startup():
    await database.connect()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Register endpoint
@app.post("/register/", response_model=UserOut)
async def register(user_in: UserIn):
    query = users_table.select().where(users_table.c.username == user_in.username)
    existing_user = await database.fetch_one(query)
    
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    hashed_password = get_password_hash(user_in.password)
    query = users_table.insert().values(username=user_in.username, hashed_password=hashed_password)
    await database.execute(query)
    
    return UserOut(username=user_in.username)

# Login endpoint
@app.post("/login/", response_model=Token)
async def login(user_in: UserIn):
    query = users_table.select().where(users_table.c.username == user_in.username)
    user = await database.fetch_one(query)
    
    if not user or not verify_password(user_in.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user_in.username})
    return {"access_token": access_token, "token_type": "bearer"}

