from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.auth import router
from backend.database import create_db_and_tables
from backend.diary import router as diary_router
from backend.psychometrics import psychometric_router
from backend.chatbot import chatbot_router
from backend.quiz import router as quiz_router
from backend.recommendations import recommendation_router

# 🧠 Startup & Shutdown logic using lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()  # This replaces @app.on_event("startup")
    yield
    # If you need to add shutdown tasks, do them after `yield`

app = FastAPI(lifespan=lifespan)

# Routers
app.include_router(router) 
app.include_router(diary_router)
app.include_router(psychometric_router)
app.include_router(chatbot_router)
app.include_router(quiz_router)
app.include_router(recommendation_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
def home():
    return {"message": "Mental Health Tracker API is running"}
