import pandas as pd
import numpy as np
import random
import os

# Set seed for reproducibility
np.random.seed(42)

# Define data components
# Define data components
job_titles = [
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

locations = ["Remote", "New York, NY", "San Francisco, CA", "Austin, TX", "London, UK", "Berlin, Germany", "Bangalore, India", "Toronto, Canada", "Sydney, Australia", "Singapore"]
companies = ["TechCorp", "DataFlow", "AI Innovations", "CloudSystems", "Insightly", "ScaleAI", "FutureLogix", "WebNexus", "AlphaSolutions", "NextGen Tech"]

# Expanded skills pool
skills_pool = [
    "Python", "SQL", "Java", "C++", "C#", "JavaScript", "TypeScript", "React", "Node.js", "Angular", "Vue.js",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins", "CI/CD",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Pandas", "NumPy", "Scikit-learn",
    "Figma", "Adobe XD", "Sketch", "UI/UX Design", "Wireframing",
    "Blockchain", "Solidity", "Smart Contracts", "Cryptography",
    "Swift", "Kotlin", "Flutter", "React Native", "iOS", "Android",
    "Unity", "Unreal Engine", "C#", "3D Math", "Game Design",
    "Cybersecurity", "Penetration Testing", "Network Security", "Firewalls", "SIEM",
    "Scrum", "Agile", "Jira", "Project Management", "Product Strategy",
    "Linux", "Shell Scripting", "Networking", "TCP/IP", "System Administration"
]

experience_levels = ["Entry-level", "Mid-level", "Senior-level", "Executive"]

def generate_skills(title):
    num_skills = random.randint(4, 9)
    base_skills = []
    
    # Specific logic for roles
    if "Data" in title or "Scientist" in title or "Big Data" in title:
        base_skills = ["Python", "SQL", "Pandas", "Machine Learning"]
    elif "ML" in title or "AI" in title or "Computer Vision" in title or "NLP" in title:
        base_skills = ["Python", "TensorFlow", "PyTorch", "Deep Learning"]
    elif "Frontend" in title or "Web" in title:
        base_skills = ["JavaScript", "React", "HTML/CSS", "TypeScript"]
    elif "Backend" in title:
        base_skills = ["Python", "Java", "Node.js", "SQL", "API Design"]
    elif "Full Stack" in title:
        base_skills = ["JavaScript", "React", "Node.js", "SQL", "AWS"]
    elif "DevOps" in title or "Reliability" in title or "Cloud" in title:
        base_skills = ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD"]
    elif "Game" in title or "AR/VR" in title:
        base_skills = ["C++", "C#", "Unity", "Unreal Engine", "3D Math"]
    elif "Mobile" in title:
        base_skills = ["Swift", "Kotlin", "React Native", "Flutter"]
    elif "Security" in title or "Cyber" in title:
        base_skills = ["Cybersecurity", "Network Security", "Linux", "Python"]
    elif "Manager" in title or "Scrum" in title:
        base_skills = ["Agile", "Scrum", "Jira", "Communication", "Leadership"]
    elif "UX" in title or "Designer" in title:
        base_skills = ["Figma", "UI/UX Design", "Wireframing", "Prototyping"]
    
    # Add random skills from pool
    remaining_slots = num_skills - len(base_skills)
    if remaining_slots > 0:
        base_skills.extend(random.sample(skills_pool, remaining_slots))
    
    return "|".join(list(set(base_skills)))

def calculate_salary(title, exp, location):
    # Base salary in INR (e.g., 5,00,000 for freshers)
    base_salary = 500000 
    
    if "Mid-level" in exp: base_salary += 700000        # ~12 LPA base
    if "Senior-level" in exp: base_salary += 1800000    # ~23 LPA base
    if "Executive" in exp: base_salary += 4000000       # ~45 LPA base
    
    # Role Premiums
    if any(x in title for x in ["AI", "ML", "Machine Learning", "Architect", "Manager"]): base_salary += 300000
    if "Data" in title or "Engineer" in title or "Full Stack" in title: base_salary += 150000
    
    # Location Multipliers (Cost of Living / Market Rate)
    # International locations converted to simplified high-tier INR equivalent for consistency in "LPA" view
    if any(c in location for c in ["San Francisco", "New York", "London", "Singapore"]): 
        base_salary *= 2.5 # International roles pay significantly higher
    elif any(c in location for c in ["Bangalore", "Berlin", "Sydney", "Toronto"]): 
        base_salary *= 1.4 # Tier 1 Tech Hubs
    elif "Remote" in location: 
        base_salary *= 1.2 # Competitive remote baseline
        
    # Add noise
    noise = np.random.normal(0, 100000)
    final_salary = base_salary + noise
    
    # Ensure minimum wage floor (e.g. 3 LPA)
    return max(int(final_salary), 300000)

# Generate dataset
num_rows = 5000
data = []

for _ in range(num_rows):
    title = random.choice(job_titles)
    exp = random.choice(experience_levels)
    loc = random.choice(locations)
    comp = random.choice(companies)
    skills = generate_skills(title)
    salary = calculate_salary(title, exp, loc)
    
    data.append({
        "role": title,
        "company": comp,
        "location": loc,
        "experience_years": random.randint(1, 15) if exp != "Entry-level" else random.randint(0, 2),
        "skills": skills,
        "salary_lpa": round(salary / 100000, 2), # Correct conversion: 15,00,000 -> 15.0 LPA
        "post_date": pd.Timestamp.now() - pd.Timedelta(days=random.randint(0, 90))
    })

df = pd.DataFrame(data)

# Save to CSV - matching the file expected by train.py
os.makedirs("data", exist_ok=True)
df.to_csv("data/job_market_analytics_dataset.csv", index=False)
print("Synthetic dataset generated and saved to data/job_market_analytics_dataset.csv")
