# app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
import datetime

Base = declarative_base()

class TimestampMixin:
    """Mixin for adding timestamp fields to models"""
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def update_updated_at_column():
    """Function for the updated_at trigger"""
    return datetime.datetime.utcnow()