from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/ml_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Prometheus metrics
achievements_counter = Counter('achievements_earned_total', 'Total achievements earned', ['achievement_type'])
badges_counter = Counter('badges_awarded_total', 'Total badges awarded', ['badge_type'])
points_histogram = Histogram('user_points_distribution', 'Distribution of user points')

# Database Models
class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    achievement_type = Column(String)
    title = Column(String)
    description = Column(Text)
    points = Column(Integer)
    icon = Column(String)
    date_earned = Column(DateTime, default=datetime.utcnow)
    campaign_id = Column(String, nullable=True)

class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    badge_type = Column(String)
    title = Column(String)
    description = Column(Text)
    level = Column(Integer, default=1)
    icon = Column(String)
    date_earned = Column(DateTime, default=datetime.utcnow)
    requirements_met = Column(Boolean, default=True)

class UserRanking(Base):
    __tablename__ = "user_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, unique=True)
    username = Column(String)
    total_points = Column(Integer, default=0)
    achievements_count = Column(Integer, default=0)
    badges_count = Column(Integer, default=0)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    rank_position = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class AchievementCreate(BaseModel):
    user_id: str
    achievement_type: str
    title: str
    description: str
    points: int
    icon: str
    campaign_id: Optional[str] = None

class BadgeCreate(BaseModel):
    user_id: str
    badge_type: str
    title: str
    description: str
    level: int = 1
    icon: str

class AchievementResponse(BaseModel):
    id: int
    user_id: str
    achievement_type: str
    title: str
    description: str
    points: int
    icon: str
    date_earned: datetime
    campaign_id: Optional[str]

class BadgeResponse(BaseModel):
    id: int
    user_id: str
    badge_type: str
    title: str
    description: str
    level: int
    icon: str
    date_earned: datetime

class UserRankingResponse(BaseModel):
    id: int
    user_id: str
    username: str
    total_points: int
    achievements_count: int
    badges_count: int
    level: int
    experience: int
    rank_position: int
    last_updated: datetime

class LeaderboardResponse(BaseModel):
    rankings: List[UserRankingResponse]
    user_rank: Optional[UserRankingResponse]

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Gamification Service", 
    description="Sistema de gamificação com conquistas, emblemas e rankings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gamification"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# Achievement endpoints
@app.post("/achievements", response_model=AchievementResponse)
async def create_achievement(achievement: AchievementCreate, db: Session = Depends(get_db)):
    """Criar nova conquista para usuário"""
    try:
        db_achievement = Achievement(**achievement.dict())
        db.add(db_achievement)
        db.commit()
        db.refresh(db_achievement)
        
        # Update metrics
        achievements_counter.labels(achievement_type=achievement.achievement_type).inc()
        
        # Update user ranking
        await update_user_ranking(achievement.user_id, achievement.points, db)
        
        logger.info(f"Achievement created: {achievement.title} for user {achievement.user_id}")
        return db_achievement
    except Exception as e:
        logger.error(f"Error creating achievement: {e}")
        raise HTTPException(status_code=500, detail="Error creating achievement")

@app.get("/achievements/{user_id}", response_model=List[AchievementResponse])
async def get_user_achievements(user_id: str, db: Session = Depends(get_db)):
    """Buscar conquistas do usuário"""
    achievements = db.query(Achievement).filter(Achievement.user_id == user_id).all()
    return achievements

@app.get("/achievements", response_model=List[AchievementResponse])
async def get_all_achievements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Buscar todas as conquistas"""
    achievements = db.query(Achievement).offset(skip).limit(limit).all()
    return achievements

# Badge endpoints
@app.post("/badges", response_model=BadgeResponse)
async def create_badge(badge: BadgeCreate, db: Session = Depends(get_db)):
    """Criar novo emblema para usuário"""
    try:
        db_badge = Badge(**badge.dict())
        db.add(db_badge)
        db.commit()
        db.refresh(db_badge)
        
        # Update metrics
        badges_counter.labels(badge_type=badge.badge_type).inc()
        
        # Update user ranking (badges give 50 points each)
        await update_user_ranking(badge.user_id, 50, db)
        
        logger.info(f"Badge created: {badge.title} for user {badge.user_id}")
        return db_badge
    except Exception as e:
        logger.error(f"Error creating badge: {e}")
        raise HTTPException(status_code=500, detail="Error creating badge")

@app.get("/badges/{user_id}", response_model=List[BadgeResponse])
async def get_user_badges(user_id: str, db: Session = Depends(get_db)):
    """Buscar emblemas do usuário"""
    badges = db.query(Badge).filter(Badge.user_id == user_id).all()
    return badges

@app.get("/badges", response_model=List[BadgeResponse])
async def get_all_badges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Buscar todos os emblemas"""
    badges = db.query(Badge).offset(skip).limit(limit).all()
    return badges

# Ranking endpoints
@app.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(limit: int = 10, user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Obter ranking de usuários"""
    try:
        # Get top users
        top_users = db.query(UserRanking).order_by(UserRanking.total_points.desc()).limit(limit).all()
        
        # Update rank positions
        for i, user in enumerate(top_users):
            user.rank_position = i + 1
        
        db.commit()
        
        # Get specific user rank if requested
        user_rank = None
        if user_id:
            user_rank = db.query(UserRanking).filter(UserRanking.user_id == user_id).first()
            if user_rank:
                # Calculate user position
                higher_ranks = db.query(UserRanking).filter(
                    UserRanking.total_points > user_rank.total_points
                ).count()
                user_rank.rank_position = higher_ranks + 1
        
        return LeaderboardResponse(rankings=top_users, user_rank=user_rank)
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Error getting leaderboard")

@app.get("/ranking/{user_id}", response_model=UserRankingResponse)
async def get_user_ranking(user_id: str, db: Session = Depends(get_db)):
    """Obter ranking de usuário específico"""
    user_ranking = db.query(UserRanking).filter(UserRanking.user_id == user_id).first()
    if not user_ranking:
        raise HTTPException(status_code=404, detail="User ranking not found")
    return user_ranking

# Helper functions
async def update_user_ranking(user_id: str, points: int, db: Session):
    """Atualizar ranking do usuário"""
    try:
        user_ranking = db.query(UserRanking).filter(UserRanking.user_id == user_id).first()
        
        if not user_ranking:
            # Create new user ranking
            user_ranking = UserRanking(
                user_id=user_id,
                username=f"User_{user_id[:8]}",
                total_points=points,
                achievements_count=1 if points > 50 else 0,
                badges_count=1 if points == 50 else 0,
                experience=points,
                level=1
            )
            db.add(user_ranking)
        else:
            # Update existing ranking
            user_ranking.total_points += points
            user_ranking.experience += points
            if points > 50:  # Achievement
                user_ranking.achievements_count += 1
            else:  # Badge
                user_ranking.badges_count += 1
            
            # Level up logic
            user_ranking.level = max(1, user_ranking.total_points // 1000)
            user_ranking.last_updated = datetime.utcnow()
        
        # Update metrics
        points_histogram.observe(user_ranking.total_points)
        
        db.commit()
        logger.info(f"Updated ranking for user {user_id}: {user_ranking.total_points} points")
        
    except Exception as e:
        logger.error(f"Error updating user ranking: {e}")
        db.rollback()

# Predefined achievement types
@app.post("/achievements/campaign-success")
async def award_campaign_success(user_id: str, campaign_id: str, roi: float, db: Session = Depends(get_db)):
    """Dar conquista por sucesso em campanha"""
    achievement = AchievementCreate(
        user_id=user_id,
        achievement_type="campaign_success",
        title="Campanha Bem-sucedida",
        description=f"ROI de {roi:.2f}% alcançado!",
        points=100,
        icon="🎯",
        campaign_id=campaign_id
    )
    return await create_achievement(achievement, db)

@app.post("/achievements/markup-master")
async def award_markup_master(user_id: str, profit_margin: float, db: Session = Depends(get_db)):
    """Dar conquista por otimização de markup"""
    achievement = AchievementCreate(
        user_id=user_id,
        achievement_type="markup_master",
        title="Mestre do Markup",
        description=f"Margem de {profit_margin:.1f}% otimizada!",
        points=150,
        icon="💰"
    )
    return await create_achievement(achievement, db)

@app.post("/badges/ai-optimizer")
async def award_ai_optimizer(user_id: str, optimizations: int, db: Session = Depends(get_db)):
    """Dar emblema por uso de IA"""
    badge = BadgeCreate(
        user_id=user_id,
        badge_type="ai_optimizer",
        title="Otimizador IA",
        description=f"{optimizations} otimizações com IA",
        level=min(5, optimizations // 10),
        icon="🤖"
    )
    return await create_badge(badge, db)

@app.post("/badges/competition-master")
async def award_competition_master(user_id: str, competitions_won: int, db: Session = Depends(get_db)):
    """Dar emblema por vitórias em concorrência"""
    badge = BadgeCreate(
        user_id=user_id,
        badge_type="competition_master",
        title="Mestre da Concorrência",
        description=f"{competitions_won} vitórias na concorrência",
        level=min(5, competitions_won // 5),
        icon="🏆"
    )
    return await create_badge(badge, db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)