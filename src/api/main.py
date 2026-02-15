from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from typing import List, Optional
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="AI Job Market Intelligence & Recruitment API")

# Load models and artifacts
try:
    model = joblib.load("src/models/salary_model.pkl")
    le_role = joblib.load("src/models/le_role.pkl")
    le_loc = joblib.load("src/models/le_loc.pkl")
    mlb = joblib.load("src/models/mlb_skills.pkl")
    feature_columns = joblib.load("src/models/feature_columns.pkl")
    skill_freq = joblib.load("src/models/skill_recommendation_data.pkl")
    
    # Candidate data
    vectorizer = joblib.load("src/models/candidate_vectorizer.pkl")
    candidate_matrix = joblib.load("src/models/candidate_matrix.pkl")
    df_candidates = pd.read_csv("data/candidates.csv")
    
except Exception as e:
    print(f"Error loading models: {e}")

class PredictionRequest(BaseModel):
    role: str
    location: str
    experience_years: float
    skills: List[str]

class PredictionResponse(BaseModel):
    predicted_salary_lpa: float

class RecommendationRequest(BaseModel):
    target_role: str
    current_skills: List[str]

class CandidateMatchRequest(BaseModel):
    skills_required: List[str]
    top_n: int = 10

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Job Market & Recruitment API"}

@app.post("/predict_salary", response_model=PredictionResponse)
def predict_salary(req: PredictionRequest):
    try:
        def safe_encode(le, val):
            try:
                return le.transform([val])[0]
            except:
                return 0

        role_enc = safe_encode(le_role, req.role)
        loc_enc = safe_encode(le_loc, req.location)
        
        # Skill encoding
        skill_vector = mlb.transform([req.skills])
        skills_df = pd.DataFrame(skill_vector, columns=[f"Skill_{s}" for s in mlb.classes_])
        
        # Prepare input df
        input_data = pd.DataFrame([[role_enc, loc_enc, req.experience_years]], 
                                  columns=['Role_Enc', 'Loc_Enc', 'experience_years'])
        full_input = pd.concat([input_data, skills_df], axis=1)
        
        # Ensure parity with training features
        for col in feature_columns:
            if col not in full_input.columns:
                full_input[col] = 0
        
        full_input = full_input[feature_columns]
        
        prediction = model.predict(full_input)[0]
        return PredictionResponse(predicted_salary_lpa=round(prediction, 2))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend_skills")
def recommend_skills(req: RecommendationRequest):
    try:
        job_skills = skill_freq[skill_freq['role'] == req.target_role]
        if job_skills.empty:
            return {"recommended_skills": [], "message": "Role not found in training data"}
        
        recommendations = job_skills[~job_skills['Skills_List'].isin(req.current_skills)]
        recommendations = recommendations.sort_values(by='count', ascending=False)
        
        return {
            "target_role": req.target_role,
            "recommended_skills": recommendations['Skills_List'].head(5).tolist(),
            "top_market_skills": job_skills.sort_values(by='count', ascending=False)['Skills_List'].head(10).tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/match_candidates")
def match_candidates(req: CandidateMatchRequest):
    try:
        # Transform the required skills into vector
        query_text = " ".join(req.skills_required)
        query_vec = vectorizer.transform([query_text])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, candidate_matrix).flatten()
        
        # Get top indices
        top_indices = similarities.argsort()[-req.top_n:][::-1]
        
        top_candidates = df_candidates.iloc[top_indices].copy()
        top_candidates['Match Score'] = np.round(similarities[top_indices] * 100, 2)
        
        return top_candidates[['Candidate ID', 'Name', 'Email', 'Experience Level', 'Skills', 'Match Score']].to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
