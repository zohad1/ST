# app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
import datetime

Base = declarative_base()

# Function for the updated_at trigger
# This is a Python representation of the DB trigger logic
# It's good practice to have it here for consistency, though the DB handles it.
def update_updated_at_column():
    return datetime.datetime.now(datetime.timezone.utc) # Use UTC for consistency
