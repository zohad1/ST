from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
import datetime

Base = declarative_base()

def update_updated_at_column():
    return datetime.datetime.now(datetime.timezone.utc)
