import os
import random
import pandas as pd
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Define careers and their corresponding pools of features
CAREER_POOLS = {
    "Data Scientist": {
        "technical_skills": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Spark", "Tableau", "Hadoop"],
        "programming_languages": ["Python", "R", "SQL", "Scala"],
        "soft_skills": ["Problem-solving", "Communication", "Critical Thinking", "Analytical Thinking"],
        "interests": ["Data Analysis", "Machine Learning", "Statistical Modeling", "Predictive Analytics"],
        "degrees": ["Data Science", "Computer Science", "Mathematics", "Statistics", "Physics"],
        "domains": ["Data Science", "Analytics", "Business Intelligence"],
        "career_interests": ["AI & Big Data", "Research", "Forecasting"]
    },
    "Machine Learning Engineer": {
        "technical_skills": ["Python", "C++", "TensorFlow", "PyTorch", "Scikit-learn", "Docker", "Kubernetes", "Git", "CUDA", "MLflow"],
        "programming_languages": ["Python", "C++", "Java", "SQL"],
        "soft_skills": ["Problem-solving", "Teamwork", "Adaptability", "Attention to Detail"],
        "interests": ["Neural Networks", "Deep Learning", "Model Deployment", "Artificial Intelligence", "Coding"],
        "degrees": ["Computer Science", "Artificial Intelligence", "Data Science", "Software Engineering"],
        "domains": ["Machine Learning", "Artificial Intelligence", "DevOps"],
        "career_interests": ["Deep Learning", "MLOps", "Computer Vision", "NLP"]
    },
    "Frontend Developer": {
        "technical_skills": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue", "Figma", "Git", "Webpack", "TailwindCSS", "Sass"],
        "programming_languages": ["JavaScript", "TypeScript", "HTML/CSS"],
        "soft_skills": ["Teamwork", "Communication", "Creativity", "Time Management"],
        "interests": ["UI/UX", "Designing UI", "Web Applications", "Visual Arts", "Coding"],
        "degrees": ["Computer Science", "Information Technology", "Web Development", "Graphic Design"],
        "domains": ["Web Development", "Design", "Frontend Engineering"],
        "career_interests": ["Web Design", "Single Page Apps", "Interactive UI"]
    },
    "Backend Developer": {
        "technical_skills": ["Java", "Python", "Go", "Node.js", "SQL", "MongoDB", "PostgreSQL", "Redis", "Docker", "Git", "APIs", "Django", "Spring Boot"],
        "programming_languages": ["Java", "Python", "Go", "SQL", "JavaScript"],
        "soft_skills": ["Problem-solving", "Critical Thinking", "Teamwork", "Attention to Detail"],
        "interests": ["Database Management", "API Design", "System Architecture", "Server Logic", "Coding"],
        "degrees": ["Computer Science", "Software Engineering", "Information Technology", "Computer Engineering"],
        "domains": ["Web Development", "Software Engineering", "Backend Engineering"],
        "career_interests": ["Scalable Systems", "Microservices", "API Development"]
    },
    "DevOps Engineer": {
        "technical_skills": ["Docker", "Kubernetes", "Linux", "Bash", "Jenkins", "CI/CD", "AWS", "Terraform", "Ansible", "Git", "Prometheus", "Grafana"],
        "programming_languages": ["Bash", "Python", "Go", "YAML"],
        "soft_skills": ["Problem-solving", "Adaptability", "Collaboration", "Time Management"],
        "interests": ["Automation", "System Admin", "Infrastructure as Code", "CI/CD Pipelines", "Monitoring"],
        "degrees": ["Computer Science", "Systems Engineering", "Information Technology"],
        "domains": ["DevOps", "Cloud Infrastructure", "System Administration"],
        "career_interests": ["Automation", "Continuous Integration", "Site Reliability"]
    },
    "Cloud Architect": {
        "technical_skills": ["AWS", "Azure", "GCP", "Terraform", "Kubernetes", "Docker", "Networking", "System Design", "Cloud Security", "Git"],
        "programming_languages": ["Python", "Go", "Bash", "SQL"],
        "soft_skills": ["Leadership", "Communication", "Strategic Thinking", "Problem-solving"],
        "interests": ["Cloud Infrastructure", "System Design", "Scalability", "Networking", "Enterprise Architecture"],
        "degrees": ["Computer Science", "Information Technology", "Cloud Computing", "Computer Engineering"],
        "domains": ["Cloud Computing", "Enterprise Solutions", "Infrastructure"],
        "career_interests": ["Cloud Migration", "Serverless Architecture", "Distributed Systems"]
    },
    "Cyber Security Analyst": {
        "technical_skills": ["Linux", "Cryptography", "Network Security", "Wireshark", "Penetration Testing", "IAM", "Firewalls", "Metasploit", "SIEM", "Nmap"],
        "programming_languages": ["Python", "Bash", "C", "SQL"],
        "soft_skills": ["Attention to Detail", "Critical Thinking", "Problem-solving", "Communication"],
        "interests": ["Ethical Hacking", "Threat Intelligence", "Network Analysis", "Cyber Defense", "Cryptography"],
        "degrees": ["Cyber Security", "Computer Science", "Information Security", "Network Engineering"],
        "domains": ["Cyber Security", "Network Security", "Risk Assessment"],
        "career_interests": ["Ethical Hacking", "Incident Response", "Security Auditing"]
    },
    "Database Administrator": {
        "technical_skills": ["SQL", "Oracle", "MySQL", "PostgreSQL", "Database Tuning", "Backup & Recovery", "Data Warehousing", "NoSQL", "Git"],
        "programming_languages": ["SQL", "PL/SQL", "Bash", "Python"],
        "soft_skills": ["Attention to Detail", "Problem-solving", "Reliability", "Analytical Thinking"],
        "interests": ["Database Management", "Performance Tuning", "Data Integrity", "SQL Querying", "Data Storage"],
        "degrees": ["Computer Science", "Information Technology", "Information Systems", "Databases"],
        "domains": ["Database Administration", "Storage Systems", "Data Architecture"],
        "career_interests": ["Data Optimization", "High Availability", "Database Security"]
    },
    "UI/UX Designer": {
        "technical_skills": ["Figma", "Sketch", "Adobe XD", "Wireframing", "Prototyping", "User Research", "Visual Design", "Interaction Design", "Illustrator"],
        "programming_languages": ["None", "HTML/CSS", "JavaScript"],
        "soft_skills": ["Creativity", "Empathy", "Communication", "Collaboration"],
        "interests": ["Design Thinking", "Wireframing", "UX Research", "Designing UI", "User Testing", "Visual Styling"],
        "degrees": ["Design", "Interaction Design", "Graphic Design", "Human-Computer Interaction", "Computer Science"],
        "domains": ["UI/UX Design", "HCI", "Product Design"],
        "career_interests": ["User-centered Design", "Interaction Flow", "Visual Mockups"]
    },
    "Product Manager": {
        "technical_skills": ["Product Strategy", "Agile", "Scrum", "Roadmapping", "Market Research", "Jira", "Trello", "Analytics", "A/B Testing"],
        "programming_languages": ["None", "SQL", "Python"],
        "soft_skills": ["Leadership", "Communication", "Conflict Resolution", "Negotiation", "Time Management"],
        "interests": ["Product Lifecycle", "User Feedback", "Market Trends", "Business Strategy", "Team Coordination"],
        "degrees": ["Business Administration", "Computer Science", "Project Management", "Marketing", "Engineering Management"],
        "domains": ["Product Management", "Business Strategy", "Project Management"],
        "career_interests": ["Product Growth", "Agile Product Owner", "Customer Experience"]
    },
    "Data Analyst": {
        "technical_skills": ["SQL", "Excel", "Tableau", "PowerBI", "Python", "Data Visualization", "SAS", "Statistics", "Reporting"],
        "programming_languages": ["SQL", "Python", "R"],
        "soft_skills": ["Communication", "Analytical Thinking", "Critical Thinking", "Problem-solving"],
        "interests": ["Business Analysis", "Reporting", "Data Visualization", "SQL Querying", "Trend Analysis"],
        "degrees": ["Computer Science", "Mathematics", "Business Administration", "Economics", "Statistics"],
        "domains": ["Business Intelligence", "Analytics", "Operations"],
        "career_interests": ["Business Analytics", "Metric Dashboarding", "Reporting Analytics"]
    }
}

EDUCATION_LEVELS = ["High School", "Associate", "Bachelor's", "Master's", "PhD"]
JOB_TYPES = ["Full-time", "Part-time", "Remote", "Contract", "Internship"]

def generate_profile(career):
    pool = CAREER_POOLS[career]
    
    # Select education and degree
    education = np.random.choice(
        EDUCATION_LEVELS, 
        p=[0.05, 0.10, 0.60, 0.20, 0.05]  # Most have Bachelor's or Master's
    )
    
    # Match degree
    if education in ["High School", "Associate"]:
        degree = "None"
    else:
        degree = random.choice(pool["degrees"])
        
    # Generate years of experience
    if education == "High School":
        years_exp = random.randint(0, 5)
    elif education == "Bachelor's":
        years_exp = random.randint(0, 10)
    elif education == "Master's":
        years_exp = random.randint(0, 12)
    else:
        years_exp = random.randint(0, 15)
        
    # Technical skills: choose 3-6 from the career pool, and maybe 0-2 random skills from other pools
    num_tech = random.randint(3, 6)
    tech_skills = random.sample(pool["technical_skills"], min(num_tech, len(pool["technical_skills"])))
    
    # 30% chance to add 1-2 random skills from other pools to create noise
    if random.random() < 0.3:
        other_careers = [c for c in CAREER_POOLS.keys() if c != career]
        other_pool = CAREER_POOLS[random.choice(other_careers)]
        other_skills = [s for s in other_pool["technical_skills"] if s not in tech_skills]
        if other_skills:
            tech_skills.extend(random.sample(other_skills, min(random.randint(1, 2), len(other_skills))))
            
    # Programming languages: choose 1-3 from pool
    num_lang = random.randint(1, 3)
    languages = random.sample(pool["programming_languages"], min(num_lang, len(pool["programming_languages"])))
    if "None" in languages and len(languages) > 1:
        languages.remove("None")
        
    # Soft skills: choose 2-4 from pool
    num_soft = random.randint(2, 4)
    soft_skills = random.sample(pool["soft_skills"], min(num_soft, len(pool["soft_skills"])))
    
    # Interests: choose 2-4 from pool
    num_interests = random.randint(2, 4)
    interests = random.sample(pool["interests"], min(num_interests, len(pool["interests"])))
    
    # Preferred domain: choose 1 from pool
    domain = random.choice(pool["domains"])
    
    # Job type: random
    job_type = random.choice(JOB_TYPES)
    
    # Career interests: choose 1-2 from pool
    num_car_int = random.randint(1, 2)
    career_int = random.sample(pool["career_interests"], min(num_car_int, len(pool["career_interests"])))
    
    return {
        "education_level": education,
        "degree_branch": degree,
        "years_of_experience": years_exp,
        "technical_skills": ", ".join(tech_skills),
        "programming_languages": ", ".join(languages),
        "soft_skills": ", ".join(soft_skills),
        "interests": ", ".join(interests),
        "preferred_domain": domain,
        "preferred_job_type": job_type,
        "career_interests": ", ".join(career_int),
        "career_role": career
    }

def main():
    data = []
    num_samples_per_career = 120
    
    for career in CAREER_POOLS.keys():
        for _ in range(num_samples_per_career):
            data.append(generate_profile(career))
            
    # Add a bit of complete noise (e.g. 5% random shuffling or completely random records)
    # to test model robustness
    df = pd.DataFrame(data)
    
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Make sure output directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save dataset
    dataset_path = "data/career_dataset.csv"
    df.to_csv(dataset_path, index=False)
    print(f"Generated dataset with {len(df)} records at {dataset_path}")
    print(f"Number of target classes: {df['career_role'].nunique()}")
    print("Class distribution:")
    print(df['career_role'].value_counts())

if __name__ == "__main__":
    main()
