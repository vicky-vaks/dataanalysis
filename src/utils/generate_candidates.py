import pandas as pd
import numpy as np
import random
import os

# Set seed for reproducibility
np.random.seed(42)

# Data for candidates
names = ["Aarav", "Aditi", "Arjun", "Ananya", "Ishaan", "Kavya", "Mohan", "Priya", "Rahul", "Sanya", 
         "Vikram", "Zoya", "Liam", "Emma", "Noah", "Olivia", "James", "Sophia", "Lucas", "Mia"]
surnames = ["Sharma", "Verma", "Gupta", "Malhotra", "Kapoor", "Smith", "Johnson", "Williams", "Brown", "Jones"]

skills_pool = ["Python", "Machine Learning", "Deep Learning", "SQL", "Tableau", "Power BI", "R", "Java", "Docker", "Kubernetes", "AWS", "Azure", "React", "Node.js", "Spark", "PyTorch", "TensorFlow", "Pandas", "NLP", "Computer Vision"]
experience_levels = ["Entry-level", "Mid-level", "Senior-level", "Executive"]

def generate_skills():
    num_skills = random.randint(3, 8)
    return ", ".join(random.sample(skills_pool, num_skills))

# Generate dataset
num_candidates = 50000
data = []

for i in range(num_candidates):
    name = f"{random.choice(names)} {random.choice(surnames)}"
    exp = random.choice(experience_levels)
    skills = generate_skills()
    email = f"{name.lower().replace(' ', '.')}@example.com"
    
    data.append({
        "Candidate ID": f"CAN_{1000 + i}",
        "Name": name,
        "Email": email,
        "Experience Level": exp,
        "Skills": skills,
        "Score": 0 # Placeholder for ranking
    })

df = pd.DataFrame(data)

# Save to CSV
os.makedirs("data", exist_ok=True)
df.to_csv("data/candidates.csv", index=False)
print("Synthetic candidates generated and saved to data/candidates.csv")
