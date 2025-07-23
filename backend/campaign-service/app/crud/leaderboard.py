
# app/crud/leaderboard.py
from sqlalchemy.orm import Session
from app.models.campaign import LeaderboardBonus
from app.schemas.leaderboard import LeaderboardBonusCreate
from uuid import UUID

def create_leaderboard_bonus(db: Session, leaderboard_bonus: LeaderboardBonusCreate, campaign_id: UUID):
    db_leaderboard_bonus = LeaderboardBonus(**leaderboard_bonus.model_dump(), campaign_id=campaign_id)
    db.add(db_leaderboard_bonus)
    db.commit()
    db.refresh(db_leaderboard_bonus)
    return db_leaderboard_bonus

def get_leaderboard_bonuses(db: Session, campaign_id: UUID):
    return db.query(LeaderboardBonus).filter(LeaderboardBonus.campaign_id == campaign_id).all()