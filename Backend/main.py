from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import os
import json
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, DateTime, JSON, MetaData, Table, select, insert, update, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
load_dotenv()
# Initialize FastAPI app
app = FastAPI(title="Balance Scale Addition Game API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Vercel Postgres database connection
DATABASE_URL = os.environ.get("POSTGRES_URL",os.environ.get("DATABASE_URL")) 
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database models
class GameConfigurationDB(Base):
    __tablename__ = "game_configurations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    difficulty_levels = Column(JSON, nullable=False)
    starting_level = Column(String, nullable=False)
    public = Column(Boolean, default=False)
    feedback_sensitivity = Column(Float, default=1.0)
    progression_criteria = Column(JSON, default=lambda: {})

class GameProgressDB(Base):
    __tablename__ = "game_progress"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    configuration_id = Column(String, nullable=False)
    current_level = Column(String, nullable=False)
    completed_problems = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    last_played = Column(DateTime, default=datetime.now)
    time_spent = Column(Integer, default=0)

class GameSessionDB(Base):
    __tablename__ = "game_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    configuration_id = Column(String, nullable=False)
    difficulty_level = Column(String, nullable=False)
    target_number = Column(Integer, nullable=False)
    answer_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.now)
    completed = Column(Boolean, default=False)
    success = Column(Boolean, nullable=True)

class ProblemAttemptDB(Base):
    __tablename__ = "problem_attempts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    addends = Column(JSON, nullable=False)
    sum = Column(Integer, nullable=False)
    target = Column(Integer, nullable=False)
    correct = Column(Boolean, nullable=False)
    time_taken = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Pydantic models (keeping these the same)
class Addend(BaseModel):
    min_value: int = Field(..., description="Minimum value for this addend")
    max_value: int = Field(..., description="Maximum value for this addend")

class DifficultyLevel(BaseModel):
    level_name: str = Field(..., description="Name of difficulty level")
    target_min: int = Field(..., description="Minimum target number")
    target_max: int = Field(..., description="Maximum target number")
    addends: List[Addend] = Field(..., description="Configuration for each addend")
    time_limit: Optional[int] = Field(None, description="Time limit in seconds (optional)")
    hints_available: bool = Field(True, description="Whether hints are available")

class GameConfiguration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    title: str = Field(..., description="Title of the game configuration")
    description: Optional[str] = Field(None, description="Description of the game")
    created_by: str = Field(..., description="User ID of creator")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    difficulty_levels: List[DifficultyLevel] = Field(..., description="Available difficulty levels")
    starting_level: str = Field(..., description="Name of starting difficulty level")
    public: bool = Field(False, description="Whether this configuration is public")
    feedback_sensitivity: float = Field(1.0, ge=0.1, le=10.0, description="How sensitive the scale is to imbalance")
    progression_criteria: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Criteria for progressing between difficulty levels"
    )

class GameProgress(BaseModel):
    user_id: str = Field(..., description="User ID")
    configuration_id: str = Field(..., description="Game configuration ID")
    current_level: str = Field(..., description="Current difficulty level")
    completed_problems: int = Field(0, description="Number of completed problems")
    correct_answers: int = Field(0, description="Number of correct answers")
    last_played: datetime = Field(default_factory=datetime.now)
    time_spent: int = Field(0, description="Total time spent in seconds")
    
class GameSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Session identifier")
    user_id: str = Field(..., description="User ID")
    configuration_id: str = Field(..., description="Game configuration ID")
    difficulty_level: str = Field(..., description="Current difficulty level")
    target_number: int = Field(..., description="Target number to match")
    answer_count: int = Field(0, description="Number of answer attempts")
    started_at: datetime = Field(default_factory=datetime.now)
    completed: bool = Field(False, description="Whether this session is completed")
    success: Optional[bool] = Field(None, description="Whether the session was successful")

class ProblemAttempt(BaseModel):
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    addends: List[int] = Field(..., description="Attempted addends")
    sum: int = Field(..., description="Sum of addends")
    target: int = Field(..., description="Target number")
    correct: bool = Field(..., description="Whether attempt was correct")
    time_taken: float = Field(..., description="Time taken in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)

# Modified API endpoints to use Postgres
@app.post("/game-configurations/", response_model=GameConfiguration)
async def create_game_configuration(
    config: GameConfiguration,
    db: Session = Depends(get_db)
):
    # Convert difficulty_levels to JSON-compatible format
    config_dict = config.dict()
    config_dict["difficulty_levels"] = json.dumps([level.dict() for level in config.difficulty_levels])
    
    db_config = GameConfigurationDB(**config_dict)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    # Convert back to Pydantic model
    result = config_dict.copy()
    result["difficulty_levels"] = [DifficultyLevel(**level) for level in json.loads(db_config.difficulty_levels)]
    
    return GameConfiguration(**result)

@app.get("/game-configurations/", response_model=List[GameConfiguration])
async def list_game_configurations(
    public_only: bool = False,
    db: Session = Depends(get_db)
):
    query = select(GameConfigurationDB)
    if public_only:
        query = query.where(GameConfigurationDB.public == True)
    
    results = db.execute(query).scalars().all()
    
    configs = []
    for config in results:
        config_dict = {
            "id": config.id,
            "title": config.title,
            "description": config.description,
            "created_by": config.created_by,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "difficulty_levels": [
                DifficultyLevel(**level) for level in json.loads(config.difficulty_levels)
            ],
            "starting_level": config.starting_level,
            "public": config.public,
            "feedback_sensitivity": config.feedback_sensitivity,
            "progression_criteria": config.progression_criteria
        }
        configs.append(GameConfiguration(**config_dict))
    
    return configs

@app.get("/game-configurations/{config_id}", response_model=GameConfiguration)
async def get_game_configuration(
    config_id: str,
    db: Session = Depends(get_db)
):
    config = db.query(GameConfigurationDB).filter(GameConfigurationDB.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Game configuration not found")
    
    config_dict = {
        "id": config.id,
        "title": config.title,
        "description": config.description,
        "created_by": config.created_by,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
        "difficulty_levels": [
            DifficultyLevel(**level) for level in json.loads(config.difficulty_levels)
        ],
        "starting_level": config.starting_level,
        "public": config.public,
        "feedback_sensitivity": config.feedback_sensitivity,
        "progression_criteria": config.progression_criteria
    }
    
    return GameConfiguration(**config_dict)

@app.put("/game-configurations/{config_id}", response_model=GameConfiguration)
async def update_game_configuration(
    config_id: str,
    updated_config: GameConfiguration,
    db: Session = Depends(get_db)
):
    config = db.query(GameConfigurationDB).filter(GameConfigurationDB.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Game configuration not found")
    
    # Update config with new values
    config_dict = updated_config.dict()
    config_dict["difficulty_levels"] = json.dumps([level.dict() for level in updated_config.difficulty_levels])
    config_dict["updated_at"] = datetime.now()
    
    for key, value in config_dict.items():
        setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    
    # Convert back to Pydantic model
    result = config_dict.copy()
    result["difficulty_levels"] = [DifficultyLevel(**level) for level in json.loads(config.difficulty_levels)]
    
    return GameConfiguration(**result)

@app.delete("/game-configurations/{config_id}", status_code=204)
async def delete_game_configuration(
    config_id: str,
    db: Session = Depends(get_db)
):
    config = db.query(GameConfigurationDB).filter(GameConfigurationDB.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Game configuration not found")
    
    db.delete(config)
    db.commit()
    return None

@app.post("/game-sessions/", response_model=GameSession)
async def create_game_session(
    config_id: str,
    db: Session = Depends(get_db)
):
    config = db.query(GameConfigurationDB).filter(GameConfigurationDB.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Game configuration not found")
    
    # Parse difficulty levels from JSON
    difficulty_levels = [DifficultyLevel(**level) for level in json.loads(config.difficulty_levels)]
    
    difficulty_level = config.starting_level
    
    level_config = next(
        (level for level in difficulty_levels if level.level_name == difficulty_level),
        None
    )
    
    if not level_config:
        raise HTTPException(status_code=400, detail=f"Difficulty level '{difficulty_level}' not found")
    
    import random
    target_number = random.randint(level_config.target_min, level_config.target_max)
    
    session = GameSession(
        user_id="anonymous",
        configuration_id=config_id,
        difficulty_level=difficulty_level,
        target_number=target_number
    )
    
    db_session = GameSessionDB(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return GameSession(**db_session.__dict__)

@app.post("/game-sessions/{session_id}/attempt", response_model=ProblemAttempt)
async def record_attempt(
    session_id: str,
    addends: List[int],
    time_taken: float,
    db: Session = Depends(get_db)
):
    session = db.query(GameSessionDB).filter(GameSessionDB.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    if session.completed:
        raise HTTPException(status_code=400, detail="Session already completed")
    
    total_sum = sum(addends)
    correct = total_sum == session.target_number
    
    attempt = ProblemAttempt(
        session_id=session_id,
        user_id="anonymous",
        addends=addends,
        sum=total_sum,
        target=session.target_number,
        correct=correct,
        time_taken=time_taken
    )
    
    db_attempt = ProblemAttemptDB(**attempt.dict())
    db.add(db_attempt)
    
    # Update session
    session.answer_count += 1
    if correct:
        session.completed = True
        session.success = True
    
    db.commit()
    
    return attempt

@app.get("/game-sessions/{session_id}", response_model=GameSession)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(GameSessionDB).filter(GameSessionDB.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return GameSession(**session.__dict__)

@app.post("/game-sessions/{session_id}/complete", response_model=GameSession)
async def complete_session(
    session_id: str,
    success: bool,
    db: Session = Depends(get_db)
):
    session = db.query(GameSessionDB).filter(GameSessionDB.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    if session.completed:
        raise HTTPException(status_code=400, detail="Session already completed")
    
    session.completed = True
    session.success = success
    
    db.commit()
    db.refresh(session)
    
    return GameSession(**session.__dict__)

@app.get("/progress/", response_model=List[GameProgress])
async def get_user_progress(db: Session = Depends(get_db)):
    progress = db.query(GameProgressDB).all()
    return [GameProgress(**p.__dict__) for p in progress]

@app.get("/progress/{config_id}", response_model=GameProgress)
async def get_game_progress(
    config_id: str,
    db: Session = Depends(get_db)
):
    progress = db.query(GameProgressDB).filter(
        GameProgressDB.user_id == "anonymous",
        GameProgressDB.configuration_id == config_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found for this game")
    
    return GameProgress(**progress.__dict__)

@app.get("/admin/all-progress", response_model=List[GameProgress])
async def get_all_progress(db: Session = Depends(get_db)):
    progress = db.query(GameProgressDB).all()
    return [GameProgress(**p.__dict__) for p in progress]

@app.get("/admin/user-attempts/{user_id}", response_model=List[ProblemAttempt])
async def get_user_attempts(
    target_user_id: str,
    db: Session = Depends(get_db)
):
    attempts = db.query(ProblemAttemptDB).filter(ProblemAttemptDB.user_id == target_user_id).all()
    return [ProblemAttempt(**a.__dict__) for a in attempts]

@app.post("/admin/set-admin")
async def set_admin_role(
    target_user_id: str,
    is_admin: bool
):
    return {"success": True, "message": f"User {target_user_id} admin status set to {is_admin}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)