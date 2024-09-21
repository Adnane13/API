from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


USERNAME = os.getenv("username")
PASSWORD = os.getenv("password")
PSQLADDRESS = os.getenv("psqladdress")
PSQLDB = os.getenv("psqldb") # the db to use 




# Database configuration
SQLALCHEMY_DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{PSQLADDRESS}/{PSQLDB}"

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()