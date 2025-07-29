from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50)
    email: str = Field(max_length=100)
    hashed_password: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class DiaryEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content: str
    sentiment: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class PersonalityScore(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    cluster: int
