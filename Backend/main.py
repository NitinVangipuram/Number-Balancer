from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

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


# cred = credentials.Certificate("firebase/serviceAccountKey.json")  # Replace with your Firebase credentials
# firebase_app = initialize_app(cred)

# security = HTTPBearer()

# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     try:
#         decoded_token = auth.verify_id_token(token)
#         user_id = decoded_token["uid"]
#         return user_id
#     except auth.InvalidIdTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except auth.ExpiredIdTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except auth.RevokedIdTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has been revoked",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Could not validate credentials: {str(e)}",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

# async def get_admin_user(user_id: str = Depends(get_current_user)):
#     try:
#         user = auth.get_user(user_id)
#         # Check if user has admin custom claim
#         custom_claims = user.custom_claims or {}
#         if not custom_claims.get("admin", False):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admin privileges required",
#             )
#         return user_id
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=str(e),
#             headers={"WWW-Authenticate": "Bearer"},
#         )


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


game_configs = {}
game_progress = {}
game_sessions = {}
problem_attempts = []


@app.post("/game-configurations/", response_model=GameConfiguration)
async def create_game_configuration(
    config: GameConfiguration
):
    game_configs[config.id] = config.dict()
    return config

@app.get("/game-configurations/", response_model=List[GameConfiguration])
async def list_game_configurations(
    public_only: bool = False
):
    if public_only:
        return [
            GameConfiguration(**config) for config in game_configs.values() 
            if config["public"]
        ]
    else:
        return [
            GameConfiguration(**config) for config in game_configs.values()
        ]

@app.get("/game-configurations/{config_id}", response_model=GameConfiguration)
async def get_game_configuration(
    config_id: str
):
    if config_id not in game_configs:
        raise HTTPException(status_code=404, detail="Game configuration not found")
    
    config = game_configs[config_id]
    return GameConfiguration(**config)

@app.put("/game-configurations/{config_id}", response_model=GameConfiguration)
async def update_game_configuration(
    config_id: str,
    updated_config: GameConfiguration
):
    if config_id not in game_configs:
        raise HTTPException(status_code=404, detail="Game configuration not found")
    
    updated_config.id = config_id
    updated_config.updated_at = datetime.now()
    
    game_configs[config_id] = updated_config.dict()
    return updated_config

@app.delete("/game-configurations/{config_id}", status_code=204)
async def delete_game_configuration(
    config_id: str
):
    if config_id not in game_configs:
        raise HTTPException(status_code=404, detail="Game configuration not found")
    
    del game_configs[config_id]
    return None


@app.post("/game-sessions/", response_model=GameSession)
async def create_game_session(
    config_id: str
):
    if config_id not in game_configs:
        raise HTTPException(status_code=404, detail="Game configuration not found")
    
    config = GameConfiguration(**game_configs[config_id])
    
    
    difficulty_level = config.starting_level
    
    
    level_config = next(
        (level for level in config.difficulty_levels if level.level_name == difficulty_level),
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
    
    game_sessions[session.id] = session.dict()
    return session

@app.post("/game-sessions/{session_id}/attempt", response_model=ProblemAttempt)
async def record_attempt(
    session_id: str,
    addends: List[int],
    time_taken: float
):
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = GameSession(**game_sessions[session_id])
    
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
    
    problem_attempts.append(attempt.dict())
    
   
    session.answer_count += 1
    
    if correct:
        session.completed = True
        session.success = True
    
    game_sessions[session_id] = session.dict()
    return attempt

@app.get("/game-sessions/{session_id}", response_model=GameSession)
async def get_session(
    session_id: str
):
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    return GameSession(**session)

@app.post("/game-sessions/{session_id}/complete", response_model=GameSession)
async def complete_session(
    session_id: str,
    success: bool
):
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = GameSession(**game_sessions[session_id])
    
    if session.completed:
        raise HTTPException(status_code=400, detail="Session already completed")
    
    session.completed = True
    session.success = success
    
    game_sessions[session_id] = session.dict()
    return session


@app.get("/progress/", response_model=List[GameProgress])
async def get_user_progress():
    user_progress = [
        GameProgress(**progress) 
        for progress_key, progress in game_progress.items()
    ]
    return user_progress

@app.get("/progress/{config_id}", response_model=GameProgress)
async def get_game_progress(
    config_id: str
):
    progress_key = f"anonymous_{config_id}"
    if progress_key not in game_progress:
        raise HTTPException(status_code=404, detail="No progress found for this game")
    
    return GameProgress(**game_progress[progress_key])


@app.get("/admin/all-progress", response_model=List[GameProgress])
async def get_all_progress():
    return [GameProgress(**progress) for progress in game_progress.values()]

@app.get("/admin/user-attempts/{user_id}", response_model=List[ProblemAttempt])
async def get_user_attempts(
    target_user_id: str
):
    user_attempts = [
        ProblemAttempt(**attempt) 
        for attempt in problem_attempts
        if attempt["user_id"] == target_user_id
    ]
    return user_attempts


@app.post("/admin/set-admin")
async def set_admin_role(
    target_user_id: str,
    is_admin: bool
):
    return {"success": True, "message": f"User {target_user_id} admin status set to {is_admin}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)