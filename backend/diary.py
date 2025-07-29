from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime
from typing import List

from backend.sentiment import analyze_sentiment
from backend.database import get_session
from backend.models import DiaryEntry, User
from backend.auth import get_current_user  # assuming JWT-based login

router = APIRouter(prefix="/diary", tags=["Diary"])

# Pydantic model for input
class DiaryInput(BaseModel):
    content: str

# Pydantic model for returning history
class DiaryOut(BaseModel):
    id: int
    content: str
    sentiment: str
    created_at: datetime

    class Config:
        orm_mode = True


from fastapi import HTTPException

@router.post("/submit")
def submit_diary(
    entry: DiaryInput,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    try:
        sentiment = analyze_sentiment(entry.content)

        if sentiment["label"] == "NEUTRAL":
            raise HTTPException(status_code=400, detail="Diary entry too short or not meaningful for analysis.")

        new_entry = DiaryEntry(
            user_id=user.id,
            content=entry.content,
            sentiment=sentiment["label"],
        )
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)

        return {
            "sentiment": new_entry.sentiment,
            "entry_id": new_entry.id
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/history", response_model=List[DiaryOut])
def get_diary_history(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    entries = session.exec(
        select(DiaryEntry)
        .where(DiaryEntry.user_id == user.id)
        .order_by(DiaryEntry.created_at.desc())
    ).all()

    return entries
