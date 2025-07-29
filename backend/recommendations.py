from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import DiaryEntry, PersonalityScore
from backend.psychometrics import cluster_descriptions  
import requests
import os

recommendation_router = APIRouter(prefix="/recommend", tags=["Recommendations"])

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

from backend.auth import get_current_user
from backend.models import User

from fastapi import HTTPException
import traceback

@recommendation_router.get("/user/me")
def get_dynamic_recommendation(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    try:
        diary_entry = session.exec(
            select(DiaryEntry).where(DiaryEntry.user_id == user.id)
            .order_by(DiaryEntry.created_at.desc())
        ).first()

        personality = session.exec(
            select(PersonalityScore).where(PersonalityScore.user_id == user.id)
            .order_by(PersonalityScore.id.desc())
        ).first()

        if not diary_entry or not personality:
            return {"error": "Insufficient data. Complete diary + psychometric test first."}

        sentiment = diary_entry.sentiment.upper()
        cluster = personality.cluster
        cluster_summary = cluster_descriptions.get(cluster, "Unknown personality cluster.")

        prompt = (
            f"The user recently wrote a diary expressing {sentiment.lower()} feelings. "
            f"Their personality profile matches {cluster_summary} "
            f"Based on this, provide a supportive, empathetic mental wellness recommendation for them."
        )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a compassionate mental health assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(OPENROUTER_URL, json=data, headers=headers)

        if response.status_code != 200:
            return {
                "error": f"LLM API error: {response.status_code}",
                "details": response.json()
            }

        reply = response.json()["choices"][0]["message"]["content"]

        return {
            "sentiment": sentiment,
            "cluster": cluster,
            "cluster_description": cluster_summary,
            "generated_recommendation": reply
        }

    except Exception as e:
        traceback.print_exc()  # print full error in console
        raise HTTPException(status_code=500, detail=str(e))
