import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, TargetEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

def normalize_location(loc):
    if not isinstance(loc, str): return "Remote"
    loc = loc.lower()
    if "remote" in loc: return "Remote"
    if "bengaluru" in loc or "bangalore" in loc: return "Bangalore, India"
    if "san francisco" in loc or "sf" in loc: return "San Francisco, CA"
    if "new york" in loc or "ny" in loc: return "New York, NY"
    if "austin" in loc: return "Austin, TX"
    if "london" in loc: return "London, UK"
    if "berlin" in loc: return "Berlin, Germany"
    if "singapore" in loc: return "Singapore"
    if "sydney" in loc: return "Sydney, Australia"
    if "toronto" in loc: return "Toronto, Canada"
    return loc.title()

def train_models():
    # Load Real Job Market Data
    df_jobs = pd.read_csv("data/job_market_analytics_dataset.csv")
    
    # --- 1. Salary Prediction Model ---
    # Preprocessing
    df_jobs['Skills_List'] = df_jobs['skills'].apply(lambda x: [s.strip() for s in str(x).split('|')] if pd.notnull(x) else [])
    
    # Normalize Location
    df_jobs['Normalized_Location'] = df_jobs['location'].apply(normalize_location)

    # Encode categorical features with Target Encoding (sklearn version)
    # random_state for reproducibility in smoothing
    encoder = TargetEncoder(target_type='continuous', random_state=42)
    encoder.set_output(transform="pandas")
    
    # Log-transform Salary
    df_jobs['log_salary'] = np.log1p(df_jobs['salary_lpa'])

    X_pre = df_jobs[['role', 'Normalized_Location', 'experience_years']]
    y = df_jobs['log_salary']

    # MultiLabelBinarizer for Skills
    mlb = MultiLabelBinarizer()
    skills_encoded = mlb.fit_transform(df_jobs['Skills_List'])
    skills_columns = [f"Skill_{s}" for s in mlb.classes_]
    skills_df = pd.DataFrame(skills_encoded, columns=skills_columns)
    
    X = pd.concat([X_pre, skills_df], axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit Target Encoder on TRAIN data only
    # Note: sklearn TargetEncoder expects X to be the categorical columns only
    encoder.fit(X_train[['role', 'Normalized_Location']], y_train)
    
    # Transform both
    X_train_encoded = encoder.transform(X_train[['role', 'Normalized_Location']])
    X_test_encoded = encoder.transform(X_test[['role', 'Normalized_Location']])
    
    # Add experience and skills back
    X_train_final = pd.concat([X_train_encoded.reset_index(drop=True), X_train[['experience_years']].reset_index(drop=True), 
                               X_train[skills_columns].reset_index(drop=True)], axis=1)
    
    X_test_final = pd.concat([X_test_encoded.reset_index(drop=True), X_test[['experience_years']].reset_index(drop=True),
                              X_test[skills_columns].reset_index(drop=True)], axis=1)

    # Train XGBoost Model
    model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42, n_jobs=-1)
    model.fit(X_train_final, y_train)
    
    # Evaluate
    y_pred_log = model.predict(X_test_final)
    y_pred = np.expm1(y_pred_log)
    y_test_orig = np.expm1(y_test)

    print(f"Salary Model MAE: {mean_absolute_error(y_test_orig, y_pred):.2f} LPA")
    print(f"Salary Model R2: {r2_score(y_test_orig, y_pred):.2f}")
    
    # Save Model artifacts
    os.makedirs("src/models", exist_ok=True)
    joblib.dump(model, "src/models/salary_model.pkl")
    joblib.dump(encoder, "src/models/target_encoder.pkl")
    joblib.dump(mlb, "src/models/mlb_skills.pkl")
    joblib.dump(X_train_final.columns.tolist(), "src/models/feature_columns.pkl")
    
    # --- 2. Skill Recommendation Preparation ---
    skill_job_matrix = df_jobs.explode('Skills_List')
    skill_freq = skill_job_matrix.groupby(['role', 'Skills_List']).size().reset_index(name='count')
    joblib.dump(skill_freq, "src/models/skill_recommendation_data.pkl")
    
    # --- 3. Candidate Matching Preparation ---
    df_candidates = pd.read_csv("data/candidates.csv")
    vectorizer = TfidfVectorizer()
    candidate_skills_text = df_candidates['Skills'].astype(str).str.replace(',', ' ')
    candidate_matrix = vectorizer.fit_transform(candidate_skills_text)
    
    joblib.dump(vectorizer, "src/models/candidate_vectorizer.pkl")
    joblib.dump(candidate_matrix, "src/models/candidate_matrix.pkl")
    
    print("Models and artifacts saved successfully.")

if __name__ == "__main__":
    train_models()
