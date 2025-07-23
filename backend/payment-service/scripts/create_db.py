#!/usr/bin/env python3
"""
Script to create database tables
"""
from app.core.database import engine
from app.models.base import Base
from app.models import *  # Import all models

def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
