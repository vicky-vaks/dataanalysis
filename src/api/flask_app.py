import os
import pandas as pd
import numpy as np
import joblib
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
import logging
import xgboost

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="../../frontend/dist", static_url_path="/")
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.errorhandler(404)
def not_found(e):
    # Fallback to index.html for React Router (Single Page App)
    return app.send_static_file("index.html")

# --- Configuration & Assets ---
# Use absolute paths relative to the current file to work in Vercel
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_PATH = os.path.join(BASE_DIR, "src", "models")

# Dynamic Data Path Handling for Read-Only Filesystems (e.g., Render/Vercel)
ORIGINAL_DATA_PATH = os.path.join(BASE_DIR, "data")

def get_writable_data_path():
    """
    Returns a writable directory for storing data.
    Checks if the local data directory is writable; serves as a fallback to temp if not.
    """
    if os.access(ORIGINAL_DATA_PATH, os.W_OK):
        return ORIGINAL_DATA_PATH
    else:
        # Fallback to system temp directory
        temp_dir = os.path.join(tempfile.gettempdir(), "ai_job_market_data")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

DATA_PATH = get_writable_data_path()
logger.info(f"Using DATA_PATH: {DATA_PATH}")

def load_assets():
    try:
        # Load compressed models
        assets = {
            "model": joblib.load(os.path.join(ASSETS_PATH, "salary_model.pkl")),
            "encoder": joblib.load(os.path.join(ASSETS_PATH, "target_encoder.pkl")),
            "mlb": joblib.load(os.path.join(ASSETS_PATH, "mlb_skills.pkl")),
            "feature_columns": joblib.load(os.path.join(ASSETS_PATH, "feature_columns.pkl")),
            "skill_freq": joblib.load(os.path.join(ASSETS_PATH, "skill_recommendation_data.pkl")),
            "vectorizer": joblib.load(os.path.join(ASSETS_PATH, "candidate_vectorizer.pkl")),
            "candidate_matrix": joblib.load(os.path.join(ASSETS_PATH, "candidate_matrix.pkl")),
        }
        
        # Load candidates.csv from the ORIGINAL data path (read-only is fine for initial load)
        # If a user uploads a new one, it will be saved to and read from DATA_PATH
        candidates_path = os.path.join(DATA_PATH, "candidates.csv")
        if not os.path.exists(candidates_path):
             # Fallback to original read-only source if not yet in writable path
             candidates_path = os.path.join(ORIGINAL_DATA_PATH, "candidates.csv")
             
        if os.path.exists(candidates_path):
            assets["df_candidates"] = pd.read_csv(candidates_path)
        else:
             logger.warning("candidates.csv not found in data or temp path.")
             assets["df_candidates"] = pd.DataFrame() # Empty fallback

        logger.info("ML Assets loaded successfully.")
        return assets
    except Exception as e:
        logger.error(f"Error loading assets: {e}")
        return None

print("Loading assets...", flush=True)
try:
    assets = load_assets()
    if assets:
        print("Assets loaded successfully.", flush=True)
    else:
        print("Assets failed to load (returned None).", flush=True)
except Exception as e:
    print(f"CRITICAL ERROR loading assets: {e}", flush=True)
    assets = None

# --- Helper Functions ---
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

# --- Endpoints ---

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "active", "message": "AI Job Market Flask API is running"}), 200

@app.route("/api/debug", methods=["GET"])
def debug_info():
    """Endpoint to assist with debugging deployment issues."""
    return jsonify({
        "base_dir": BASE_DIR,
        "assets_path": ASSETS_PATH,
        "original_data_path": ORIGINAL_DATA_PATH,
        "writable_data_path": DATA_PATH,
        "is_original_writable": os.access(ORIGINAL_DATA_PATH, os.W_OK),
        "assets_loaded": assets is not None,
        "cwd": os.getcwd(),
        "files_in_data": os.listdir(DATA_PATH) if os.path.exists(DATA_PATH) else "Path does not exist"
    })

@app.route("/api/market_data", methods=["GET", "POST"])
def get_market_data():
    try:
        # Check writable path first (uploaded file), then fallback to original
        csv_path = os.path.join(DATA_PATH, "job_market_analytics_dataset.csv")
        if not os.path.exists(csv_path):
             csv_path = os.path.join(ORIGINAL_DATA_PATH, "job_market_analytics_dataset.csv")

        if not os.path.exists(csv_path):
            return jsonify({"error": "Dataset not found"}), 404
        
        df = pd.read_csv(csv_path)
        
        # User can provide custom mapping via POST
        custom_mapping = {}
        if request.method == "POST" and request.is_json:
            req_data = request.json
            if req_data and "mapping" in req_data:
                custom_mapping = req_data["mapping"] or {}

        # Robust column detection (fuzzy matching)
        cols_orig = list(df.columns)
        def find_best_col(keywords):
            # 1. Exact or close match (ignoring case/spaces/underscores)
            for col in cols_orig:
                clean_col = col.lower().replace('_', '').replace(' ', '')
                for k in keywords:
                    clean_k = k.lower().replace('_', '').replace(' ', '')
                    if clean_col == clean_k:
                        return col
            # 2. Substring match
            for col in cols_orig:
                clean_col = col.lower().replace('_', '').replace(' ', '')
                for k in keywords:
                    clean_k = k.lower().replace('_', '').replace(' ', '')
                    if clean_k in clean_col or clean_col in clean_k:
                        return col
            return None

        role_col = custom_mapping.get('role') or find_best_col(['role', 'job role', 'title', 'job title', 'position', 'job name'])
        salary_col = custom_mapping.get('salary') or find_best_col(['salary', 'salary_lpa', 'compensation', 'package', 'pay', 'ctc'])
        skills_col = custom_mapping.get('skills') or find_best_col(['skills', 'skillset', 'technologies', 'requirements', 'stacks'])
        exp_col = custom_mapping.get('experience') or find_best_col(['experience', 'exp', 'years of experience', 'years', 'tenure'])

        # Essential columns (Role is the only strictly required one now, Skills highly recommended)
        if not role_col:
             return jsonify({
                "error": "mapping_required",
                "columns": list(df.columns),
                "detected": {
                    "role": role_col,
                    "salary": salary_col,
                    "skills": skills_col,
                    "experience": exp_col
                }
            }), 200

        # Helper for Role Normalization
        STANDARD_ROLES = [
            "Data Scientist", "ML Engineer", "Software Engineer", "Data Analyst",
            "Backend Developer", "Frontend Developer", "Full Stack Developer",
            "DevOps Engineer", "Cloud Architect", "AI Researcher", "Data Engineer",
            "Product Manager (Tech)", "UX Designer", "Cybersecurity Analyst",
            "Blockchain Developer", "Mobile App Developer", "Embedded Systems Engineer",
            "QA Automation Engineer", "NOC Engineer", "Solutions Architect",
            "Technical Support Engineer", "Database Administrator", "Systems Analyst",
            "Game Developer", "AR/VR Developer", "Big Data Engineer", "Scrum Master",
            "Site Reliability Engineer", "Computer Vision Engineer", "NLP Scientist"
        ]

        def normalize_role(role):
            if not isinstance(role, str): return "Other"
            role_lower = role.lower()
            # Simple fuzzy match
            best_match = "Other"
            max_score = 0
            
            for std in STANDARD_ROLES:
                # Token overlap score
                std_tokens = set(std.lower().split())
                role_tokens = set(role_lower.split())
                overlap = len(std_tokens.intersection(role_tokens))
                if overlap > max_score:
                    max_score = overlap
                    best_match = std
            
            return best_match if max_score > 0 else role.title()

        # Data Cleaning & Normalization
        if role_col:
            df['Normalized_Role'] = df[role_col].apply(normalize_role)
            unique_roles = sorted(list(set(STANDARD_ROLES) & set(df['Normalized_Role'].unique()))) + sorted(list(set(df['Normalized_Role'].unique()) - set(STANDARD_ROLES)))
        else:
            unique_roles = []

        if salary_col:
            df[salary_col] = pd.to_numeric(df[salary_col], errors='coerce').fillna(0)
        
        if exp_col:
            # Extract just the number from "5 years", "5+", etc.
            df[exp_col] = df[exp_col].astype(str).str.extract(r'(\d+)').astype(float).fillna(0).astype(int)
            unique_exp = sorted(df[exp_col].unique().tolist())
        else:
            unique_exp = []
        
        # Skill Demand
        if skills_col:
            df[skills_col] = df[skills_col].astype(str)
            all_skills = df[skills_col].apply(lambda x: [s.strip() for s in str(x).replace('|', ',').replace(';', ',').split(',')]).explode()
            skill_counts = all_skills.value_counts().head(10).reset_index()
            skill_counts.columns = ['skill', 'count']
            
            unique_skills = sorted(all_skills.dropna().unique().tolist())
        else:
            skill_counts = pd.DataFrame(columns=['skill', 'count'])
            unique_skills = []
        
        # Salary by Role (only if salary exists)
        job_salary = []
        exp_salary = []

        if salary_col:
            # Use Normalized Role for aggregation
            job_salary = df.groupby('Normalized_Role')[salary_col].mean().reset_index()
            job_salary.columns = ['title', 'salary']
            job_salary = job_salary.to_dict(orient="records")
            
            if exp_col:
                exp_salary = df.groupby(exp_col)[salary_col].mean().reset_index()
                exp_salary.columns = ['level', 'salary']
                exp_salary = exp_salary.to_dict(orient="records")

        return jsonify({
            "skill_demand": skill_counts.to_dict(orient="records"),
            "job_salary": job_salary,
            "exp_salary": exp_salary,
            "total_records": len(df),
            "filters": {
                "roles": unique_roles,
                "skills": unique_skills,
                "experience": unique_exp
            },
            "mapping": {
                "role": role_col,
                "salary": salary_col,
                "skills": skills_col,
                "experience": exp_col
            }
        })
    except Exception as e:
        logger.error(f"Market Data Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload_csv", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.lower().endswith('.csv'):
        try:
            df = pd.read_csv(file)
            # Save it as the primary dataset for analytics
            # Using the dynamic DATA_PATH which is guaranteed to be writable
            df.to_csv(os.path.join(DATA_PATH, "job_market_analytics_dataset.csv"), index=False)
            
            return jsonify({"message": "File uploaded and analyzed successfully"}), 200
        except Exception as e:
            logger.error(f"CSV Upload Failed: {e}")
            return jsonify({"error": f"Failed to process CSV: {e}"}), 500
    return jsonify({"error": "Invalid file type. Please upload a CSV."}), 400

@app.route("/api/predict_salary", methods=["POST"])
def predict_salary():
    if not assets: return jsonify({"error": "Model assets not loaded"}), 500
    data = request.json
    try:
        role = data.get("role")
        location = data.get("location")
        experience = float(data.get("experience_years", 0))
        skills = data.get("skills", [])

        # Normalize location (Critical for accuracy)
        norm_location = normalize_location(location)

        # Create input dataframe for TargetEncoder
        # Notes:
        # 1. We must use the same columns/names as passed to fit()
        # 2. TargetEncoder expects a DataFrame, not a single value usually
        input_cats = pd.DataFrame([[role, norm_location]], columns=['role', 'Normalized_Location'])
        
        # Transform using the loaded encoder
        # This returns a DataFrame with the encoded values
        cats_encoded = assets['encoder'].transform(input_cats)
        
        # Skill encoding
        s_vec = assets['mlb'].transform([skills])
        s_df = pd.DataFrame(s_vec, columns=[f"Skill_{s}" for s in assets['mlb'].classes_])
        
        # Combine everything
        # Access encoded values by column name (values are floats now)
        # Note: reset_index is needed to align indices
        i_data = pd.concat([cats_encoded.reset_index(drop=True), pd.DataFrame([[experience]], columns=['experience_years'])], axis=1)
        
        f_input = pd.concat([i_data, s_df], axis=1)
        
        # Align with training features
        for col in assets['feature_columns']:
            if col not in f_input.columns: f_input[col] = 0
        f_input = f_input[assets['feature_columns']]
        
        # Predict (Log Scale)
        prediction_log = assets['model'].predict(f_input)[0]
        
        # Inverse Log Transform (expm1)
        prediction = np.expm1(prediction_log)
        
        return jsonify({"predicted_salary": round(float(prediction), 2)})
    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/recommend_skills", methods=["POST"])
def recommend_skills():
    if not assets: return jsonify({"error": "Model assets not loaded"}), 500
    data = request.json
    try:
        target_role = data.get("target_role")
        current_skills = data.get("current_skills", [])
        
        sf = assets['skill_freq']
        job_skills = sf[sf['role'] == target_role]
        
        if job_skills.empty:
            return jsonify({
                "match_percentage": 0,
                "required_skills": [],
                "missing_skills": [],
                "matched_skills": []
            })

        # Top 30 skills constitute the "Required" set for this role
        top_skills_df = job_skills.sort_values(by='count', ascending=False).head(30)
        required_skills = top_skills_df['Skills_List'].tolist()
        required_set = set(required_skills)
        current_set = set(current_skills)
        
        matched_skills = list(required_set.intersection(current_set))
        missing_skills = list(required_set - current_set)
        
        # Calculate Percentage
        match_percentage = 0
        if required_skills:
            match_percentage = int((len(matched_skills) / len(required_skills)) * 100)

        return jsonify({
            "match_percentage": match_percentage,
            "required_skills": required_skills,
            "missing_skills": missing_skills,
            "matched_skills": matched_skills
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/get_role_skills", methods=["POST"])
def get_role_skills():
    if not assets: return jsonify({"error": "Model assets not loaded"}), 500
    try:
        target_role = request.json.get("target_role")
        sf = assets['skill_freq']
        
        # Filter for the role and get top 30 most frequent skills
        role_skills = sf[sf['role'] == target_role].sort_values(by='count', ascending=False).head(30)
        
        if role_skills.empty:
            # Fallback if no specific data for role
            return jsonify({"skills": ["Python", "SQL", "Communication", "Leadership", "Project Management"]})
            
        return jsonify({"skills": role_skills['Skills_List'].tolist()})
    except Exception as e:
         return jsonify({"error": str(e)}), 500

@app.route("/api/match_candidates", methods=["POST"])
def match_candidates():
    if not assets: return jsonify({"error": "Model assets not loaded"}), 500
    data = request.json
    try:
        skills_required = data.get("skills_required", [])
        top_n = int(data.get("top_n", 10))
        
        query_text = " ".join(skills_required)
        query_vec = assets['vectorizer'].transform([query_text])
        similarities = cosine_similarity(query_vec, assets['candidate_matrix']).flatten()
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        matches = assets['df_candidates'].iloc[top_indices].copy()
        matches['score'] = np.round(similarities[top_indices] * 100, 1)
        
        return jsonify({
            "candidates": matches[['Candidate ID', 'Name', 'Email', 'Experience Level', 'Skills', 'score']].to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
