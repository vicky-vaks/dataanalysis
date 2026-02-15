# 🚀 AI-Driven Job Market Intelligence (Full-Stack)

A premium, interactive AI system for job market intelligence. This version features a modern **Full-Stack** architecture for better performance, aesthetics, and hosting flexibility.

## ✨ Features
- **Glassmorphism Dashboard**: Interactive market overview with animated charts.
- **AI Salary Engine**: Real-time salary projection using **XGBoost** & **Target Encoding** for high accuracy.
- **Skill Gap Analysis**: Visualized career path optimization and skill recommendations.
- **Candidate Matching**: AI-driven candidate ranking using TF-IDF and Cosine Similarity.
- **Deployment Ready**: Configured for split deployment (Render Backend + Vercel Frontend).

## 🛠️ Tech Stack
- **Frontend**: React (Vite), Recharts, Lucide, Axios.
- **Backend**: Flask, Pandas, Scikit-learn, XGBoost.
- **AI/ML**: XGBoost Regressor, TargetEncoder, TF-IDF.
- **Deployment**: Render (Python), Vercel (Static/SPA).

## 🏗️ Setup & Installation

### 1. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Generate Synthetic Data (if needed) & Train Models
python src/utils/generate_data.py
python src/models/train.py

# Run Flask API
python src/api/flask_app.py
```
*API runs on http://localhost:5000*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on http://localhost:5173*

## 🚀 Deployment

### Backend (Render)
- Connect repo to Render.
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn src.api.flask_app:app`
- Env Vars: `PYTHON_VERSION=3.9.18`

### Frontend (Vercel)
- Connect repo to Vercel.
- Framework: Vite.
- Root Directory: `frontend`.
- Env Vars: `VITE_API_BASE` = `https://your-render-backend-url.onrender.com`

---
Developed by **G R VIGNESH**
