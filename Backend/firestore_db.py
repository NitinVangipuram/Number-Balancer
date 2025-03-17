# firestore_db.py
from firebase_admin import firestore
from typing import Dict, Any, List, Optional
from datetime import datetime

# Firestore DB client
db = firestore.client()

# Collection references
game_configs_ref = db.collection('game_configurations')
game_progress_ref = db.collection('game_progress')
game_sessions_ref = db.collection('game_sessions')
problem_attempts_ref = db.collection('problem_attempts')

# Game Configuration Operations
def create_game_configuration(config_data: Dict[str, Any]) -> str:
    """Create a new game configuration"""
    doc_ref = game_configs_ref.document(config_data["id"])
    doc_ref.set(config_data)
    return config_data["id"]

def get_game_configuration(config_id: str) -> Optional[Dict[str, Any]]:
    """Get a game configuration by ID"""
    doc_ref = game_configs_ref.document(config_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def update_game_configuration(config_id: str, config_data: Dict[str, Any]) -> bool:
    """Update a game configuration"""
    doc_ref = game_configs_ref.document(config_id)
    if not doc_ref.get().exists:
        return False
    
    config_data["updated_at"] = datetime.now()
    doc_ref.update(config_data)
    return True

def delete_game_configuration(config_id: str) -> bool:
    """Delete a game configuration"""
    doc_ref = game_configs_ref.document(config_id)
    if not doc_ref.get().exists:
        return False
    
    doc_ref.delete()
    return True

def list_game_configurations(user_id: str, public_only: bool = False) -> List[Dict[str, Any]]:
    """List game configurations - either all public ones or those available to a user"""
    if public_only:
        query = game_configs_ref.where("public", "==", True)
    else:
        query = game_configs_ref.where("public", "==", True)
        # This is a simplified query - in production, use Firebase compound queries
        # For now, we'll fetch all and filter
        user_configs = game_configs_ref.where("created_by", "==", user_id).stream()
        user_configs_list = [doc.to_dict() for doc in user_configs]
    
    public_configs = [doc.to_dict() for doc in query.stream()]
    
    if public_only:
        return public_configs
    
    # Combine and deduplicate
    all_configs = {config["id"]: config for config in public_configs}
    for config in user_configs_list:
        all_configs[config["id"]] = config
    
    return list(all_configs.values())

# Game Progress Operations
def get_game_progress(user_id: str, config_id: str) -> Optional[Dict[str, Any]]:
    """Get a user's progress for a specific game"""
    query = game_progress_ref.where("user_id", "==", user_id).where("configuration_id", "==", config_id)
    docs = list(query.stream())
    
    if docs:
        return docs[0].to_dict()
    return None

def update_game_progress(progress_data: Dict[str, Any]) -> str:
    """Update a user's game progress"""
    # Use composite key for document ID
    doc_id = f"{progress_data['user_id']}_{progress_data['configuration_id']}"
    doc_ref = game_progress_ref.document(doc_id)
    
    # Update if exists, create if not
    if doc_ref.get().exists:
        progress_data["last_played"] = datetime.now()
        doc_ref.update(progress_data)
    else:
        doc_ref.set(progress_data)
    
    return doc_id

def list_user_progress(user_id: str) -> List[Dict[str, Any]]:
    """List all progress entries for a user"""
    query = game_progress_ref.where("user_id", "==", user_id)
    return [doc.to_dict() for doc in query.stream()]

def list_all_progress() -> List[Dict[str, Any]]:
    """List all progress entries (admin only)"""
    return [doc.to_dict() for doc in game_progress_ref.stream()]

# Game Session Operations
def create_game_session(session_data: Dict[str, Any]) -> str:
    """Create a new game session"""
    doc_ref = game_sessions_ref.document(session_data["id"])
    doc_ref.set(session_data)
    return session_data["id"]

def get_game_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get a game session by ID"""
    doc_ref = game_sessions_ref.document(session_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def update_game_session(session_id: str, session_data: Dict[str, Any]) -> bool:
    """Update a game session"""
    doc_ref = game_sessions_ref.document(session_id)
    if not doc_ref.get().exists:
        return False
    
    doc_ref.update(session_data)
    return True

def list_user_sessions(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """List recent game sessions for a user"""
    query = game_sessions_ref.where("user_id", "==", user_id).order_by("started_at", direction=firestore.Query.DESCENDING).limit(limit)
    return [doc.to_dict() for doc in query.stream()]

# Problem Attempt Operations
def record_problem_attempt(attempt_data: Dict[str, Any]) -> str:
    """Record a problem attempt"""
    doc_ref = problem_attempts_ref.document()
    doc_ref.set(attempt_data)
    return doc_ref.id

def list_session_attempts(session_id: str) -> List[Dict[str, Any]]:
    """List all attempts for a specific session"""
    query = problem_attempts_ref.where("session_id", "==", session_id).order_by("timestamp")
    return [doc.to_dict() for doc in query.stream()]

def list_user_attempts(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """List recent attempts for a user"""
    query = problem_attempts_ref.where("user_id", "==", user_id).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
    return [doc.to_dict() for doc in query.stream()]