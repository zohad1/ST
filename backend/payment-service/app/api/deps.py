from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role

# Re-export common dependencies
__all__ = ["get_db", "get_current_user", "require_role"]
