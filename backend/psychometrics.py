from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
from collections import Counter
from sqlmodel import Session
from backend.models import PersonalityScore, User
from backend.auth import get_current_user
from backend.database import get_session
from fastapi import Depends


psychometric_router = APIRouter(prefix="/psychometrics", tags=["Psychometric"])

# Load and preprocess the trained dataset
df = pd.read_csv("data/user_traits_with_clusters.csv")

df["O"] = df[[f"OPN{i}" for i in range(1, 11)]].mean(axis=1)
df["C"] = df[[f"CSN{i}" for i in range(1, 11)]].mean(axis=1)
df["E"] = df[[f"EXT{i}" for i in range(1, 11)]].mean(axis=1)
df["A"] = df[[f"AGR{i}" for i in range(1, 11)]].mean(axis=1)
df["N"] = df[[f"EST{i}" for i in range(1, 11)]].mean(axis=1)

# Store only relevant traits + clusters
trait_df = df[["O", "C", "E", "A", "N", "Clusters"]].copy()

# Calculate cluster-wise trait averages
cluster_trait_means = trait_df.groupby("Clusters")[["O", "C", "E", "A", "N"]].mean()

def generate_cluster_description(row):
    cid = int(row.name)
    o, c, e, a, n = row["O"], row["C"], row["E"], row["A"], row["N"]

    if row.mean() < 1.0:
        return f"Cluster {cid}: Extremely low scores — likely invalid or placeholder responses."

    description = f"Cluster {cid}: "

    # Openness
    if o > 3.5:
        description += "Highly open to experience, creative and intellectually curious. "
    elif o < 2.5:
        description += "Prefers structure, tradition and familiarity. "

    # Conscientiousness
    if c > 3.5:
        description += "Organized, responsible, and goal-oriented. "
    elif c < 2.5:
        description += "More spontaneous, may struggle with routine or planning. "

    # Extraversion
    if e > 3.5:
        description += "Sociable and outgoing. "
    elif e < 2.5:
        description += "Introverted, reflective, and quiet. "

    # Agreeableness
    if a > 3.5:
        description += "Empathetic, trusting, and cooperative. "
    elif a < 2.5:
        description += "More skeptical and independent-minded. "

    # Neuroticism
    if n > 3.5:
        description += "Emotionally reactive and sensitive to stress. "
    elif n < 2.5:
        description += "Emotionally stable and resilient. "

    return description.strip()

cluster_descriptions = {
    int(i): generate_cluster_description(row)
    for i, row in cluster_trait_means.iterrows()
}

class QuizInput(BaseModel):
    q1_openness: int
    q2_openness: int
    q3_conscientiousness: int
    q4_conscientiousness: int
    q5_extraversion: int
    q6_extraversion: int
    q7_agreeableness: int
    q8_agreeableness: int
    q9_neuroticism: int
    q10_neuroticism: int

@psychometric_router.post("/quiz")
def analyze_quiz(
    data: QuizInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Calculate average trait scores
    openness = (data.q1_openness + data.q2_openness) / 2
    conscientiousness = (data.q3_conscientiousness + data.q4_conscientiousness) / 2
    extraversion = (data.q5_extraversion + data.q6_extraversion) / 2
    agreeableness = (data.q7_agreeableness + data.q8_agreeableness) / 2
    neuroticism = (data.q9_neuroticism + data.q10_neuroticism) / 2

    user_vector = [[openness, conscientiousness, extraversion, agreeableness, neuroticism]]
    distances = euclidean_distances(user_vector, trait_df[["O", "C", "E", "A", "N"]])
    min_distance = distances.min()

    tied_indices = [i for i, d in enumerate(distances[0]) if d == min_distance]
    tied_clusters = [int(trait_df.iloc[i]["Clusters"]) for i in tied_indices]
    cluster_counts = Counter(tied_clusters)
    matched_cluster = cluster_counts.most_common(1)[0][0]
    cluster_description = cluster_descriptions.get(matched_cluster, "Unknown cluster")

    # ✅ Save PersonalityScore to database
    personality_score = PersonalityScore(
        user_id=current_user.id,
        openness=openness,
        conscientiousness=conscientiousness,
        extraversion=extraversion,
        agreeableness=agreeableness,
        neuroticism=neuroticism,
        cluster=matched_cluster
    )
    session.add(personality_score)
    session.commit()
    session.refresh(personality_score)

    return {
        "input_traits": {
            "openness": openness,
            "conscientiousness": conscientiousness,
            "extraversion": extraversion,
            "agreeableness": agreeableness,
            "neuroticism": neuroticism
        },
        "matched_cluster": matched_cluster,
        "cluster_description": cluster_description,
        "distance": float(min_distance),
        "tied_clusters": tied_clusters if len(set(tied_clusters)) > 1 else None
    }
