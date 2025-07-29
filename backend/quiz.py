# backend/quiz.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
from backend.auth import get_current_user
from backend.models import User

router = APIRouter(prefix="/quiz", tags=["Quiz"])

class QuizScores(BaseModel):
    scores: Dict[str, float]

@router.post("/submit")
def submit_quiz(scores: QuizScores, user: User = Depends(get_current_user)):
    # For now, just log the result (you can save to DB if needed)
    print(f"Received quiz from {user.username}: {scores.scores}")
    return {"msg": "Quiz saved", "scores": scores.scores}
