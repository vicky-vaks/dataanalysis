import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import joblib
import os
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration ---
st.set_page_config(page_title="AI Job Market Intelligence", layout="wide")

# --- Caching Wrapper (Backwards Compatibility) ---
def get_resource_cache():
    if hasattr(st, "cache_resource"): return st.cache_resource
    return st.cache(allow_output_mutation=True)

def get_data_cache():
    if hasattr(st, "cache_data"): return st.cache_data
    return st.cache()

# --- Model & Data Loading ---
@get_resource_cache()
def load_ml_assets():
    try:
        model = joblib.load("src/models/salary_model.pkl")
        le_role = joblib.load("src/models/le_role.pkl")
        le_loc = joblib.load("src/models/le_loc.pkl")
        mlb = joblib.load("src/models/mlb_skills.pkl")
        feature_columns = joblib.load("src/models/feature_columns.pkl")
        skill_freq = joblib.load("src/models/skill_recommendation_data.pkl")
        vectorizer = joblib.load("src/models/candidate_vectorizer.pkl")
        candidate_matrix = joblib.load("src/models/candidate_matrix.pkl")
        df_candidates = pd.read_csv("data/candidates.csv")
        return {
            "model": model, "le_role": le_role, "le_loc": le_loc,
            "mlb": mlb, "feature_columns": feature_columns,
            "skill_freq": skill_freq, "vectorizer": vectorizer,
            "candidate_matrix": candidate_matrix, "df_candidates": df_candidates
        }
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None

@get_data_cache()
def load_data():
    if os.path.exists("data/job_market_analytics_dataset.csv"):
        return pd.read_csv("data/job_market_analytics_dataset.csv")
    return pd.DataFrame()

assets = load_ml_assets()
df = load_data()

# --- Side Navigation (Simple UI) ---
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Choose a Module", ["Market Overview", "Salary Predictor", "Skill Roadmap", "Recruiter View"])

st.title("🚀 AI Job Market Analytics")

if menu == "Market Overview":
    st.header("📊 Job Market Insights")
    
    if df.empty:
        st.warning("Please upload or generate the job market dataset.")
    else:
        # Key Stats
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Average Salary", f"₹{round(df['salary_lpa'].mean(), 1)} LPA")
        col_m2.metric("Median Exp", f"{round(df['experience_years'].median(), 1)} Years")
        col_m3.metric("Total Jobs Analyzed", len(df))
        
        st.markdown("---")
        
        # Clear Chart 1: Top Skills
        st.subheader("High-Demand Tech Skills")
        all_skills = df['skills'].str.split('|').explode()
        skill_counts = all_skills.value_counts().head(10).reset_index()
        skill_counts.columns = ['Skill', 'Count']
        
        fig1 = px.bar(
            skill_counts, x='Count', y='Skill', orientation='h',
            title="Top 10 Most Requested Skills (Market Demand)",
            color='Count', color_continuous_scale='Blues',
            labels={'Count': 'Number of Job Postings', 'Skill': 'Technology/Skill'}
        )
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)

        # Clear Chart 2: Salary Distribution
        st.subheader("Market Salary Distribution")
        fig2 = px.histogram(
            df, x='salary_lpa', nbins=20, marginal="box",
            title="Salary Range Prevalence (LPA)",
            color_discrete_sequence=['#1f77b4'],
            labels={'salary_lpa': 'Salary in LPA (Lakhs Per Annum)'}
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Clear Chart 3: Exp vs Salary
        st.subheader("Career Growth Trend: Experience vs Salary")
        fig3 = px.scatter(
            df, x='experience_years', y='salary_lpa', color='role',
            title="Experience (Years) vs. Expected Market Salary (LPA)",
            trendline="ols",
            labels={'experience_years': 'Years of Experience', 'salary_lpa': 'Market Value (LPA)'},
            opacity=0.7
        )
        st.plotly_chart(fig3, use_container_width=True)

elif menu == "Salary Predictor":
    st.header("💰 Salary Prediction Engine")
    if not assets: st.stop()
    
    col1, col2 = st.columns(2)
    roles = sorted(df['role'].unique()) if not df.empty else []
    locations = sorted(df['location'].unique()) if not df.empty else []
    
    with col1:
        role = st.selectbox("Position/Role", roles)
        location = st.selectbox("Job Location", locations)
        experience = st.slider("Experience Level (Years)", 0, 30, 5)
    with col2:
        all_possible_skills = sorted(list(set(df['skills'].str.split('|').explode()))) if not df.empty else []
        selected_skills = st.multiselect("Select Your Skills", all_possible_skills)
    
    if st.button("Calculate Market Value"):
        def safe_encode(le, val):
            try: return le.transform([val])[0]
            except: return 0

        r_enc = safe_encode(assets['le_role'], role)
        l_enc = safe_encode(assets['le_loc'], location)
        s_vec = assets['mlb'].transform([selected_skills])
        s_df = pd.DataFrame(s_vec, columns=[f"Skill_{s}" for s in assets['mlb'].classes_])
        
        i_data = pd.DataFrame([[r_enc, l_enc, float(experience)]], columns=['Role_Enc', 'Loc_Enc', 'experience_years'])
        f_input = pd.concat([i_data, s_df], axis=1)
        for col in assets['feature_columns']:
            if col not in f_input.columns: f_input[col] = 0
        f_input = f_input[assets['feature_columns']]
        
        prediction = assets['model'].predict(f_input)[0]
        st.success(f"### Predicted Market Salary: ₹{round(prediction, 2)} LPA")

elif menu == "Skill Roadmap":
    st.header("🎯 Talent Skill Recommendation")
    if not assets: st.stop()
    
    target_role = st.selectbox("Desired Target Role", sorted(df['role'].unique()) if not df.empty else [])
    current_skills = st.multiselect("Your Current Skills", 
                                    sorted(list(set(df['skills'].str.split('|').explode()))) if not df.empty else [])
    
    if st.button("Generate Learning Path"):
        job_skills = assets['skill_freq'][assets['skill_freq']['role'] == target_role]
        recommendations = job_skills[~job_skills['Skills_List'].isin(current_skills)].sort_values(by='count', ascending=False)
        
        st.markdown(f"**Top Missing Skills for {target_role}:**")
        for skill in recommendations['Skills_List'].head(5):
            st.info(f"💡 Recommendation: {skill}")
        
        # Skill Gap Visualization
        market_top = job_skills.sort_values(by='count', ascending=False).head(10)
        fig_gap = px.bar(
            market_top, x='count', y='Skills_List', text='count',
            title=f"Industry Standards for {target_role} Roles",
            labels={'count': 'Number of Companies Requring this Skill', 'Skills_List': 'Core Competency'}
        )
        fig_gap.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_gap, use_container_width=True)

elif menu == "Recruiter View":
    st.header("👥 AI Candidate Matching")
    if not assets: st.stop()
    
    st.write("Search the 50,000 profile database to find perfectly matched candidates.")
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        job_role_ref = st.selectbox("Search Base Template", sorted(df['role'].unique()) if not df.empty else [])
        ref_job_data = df[df['role'] == job_role_ref]
        ref_skills = ref_job_data['skills'].iloc[0].split('|') if not ref_job_data.empty else []
        search_skills = st.multiselect("Fine-tune Required Skills", 
                                       sorted(list(set(df['skills'].str.split('|').explode()))) if not df.empty else [], 
                                       default=ref_skills[:5])
        top_n = st.slider("Number of Candidates to Display", 5, 50, 10)

    with col_c2:
        if st.button("Find Top Talents"):
            query_text = " ".join(search_skills)
            query_vec = assets['vectorizer'].transform([query_text])
            similarities = cosine_similarity(query_vec, assets['candidate_matrix']).flatten()
            top_indices = similarities.argsort()[-int(top_n):][::-1]
            
            matches = assets['df_candidates'].iloc[top_indices].copy()
            matches['Score%'] = np.round(similarities[top_indices] * 100, 1)
            
            st.write(f"### Found {len(matches)} Highly Matched Profiles")
            st.table(matches[['Name', 'Experience Level', 'Score%', 'Skills']])

st.sidebar.markdown("---")
st.sidebar.info("Developed by G R VIGNESH")
