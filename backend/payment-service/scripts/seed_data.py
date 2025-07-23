#!/usr/bin/env python3
"""
Script to seed sample data
"""
from app.core.database import SessionLocal
from app.models import *  # Import all models

def seed_data():
    db = SessionLocal()
    try:
        print("Seeding sample data...")
        # Add sample data here
        print("Sample data seeded successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
