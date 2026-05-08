import pandas as pd
import re

print("=== PHASE 3: DATA CLEANING & PREPROCESSING ===\n")

# Load raw data
print("Loading raw data...")
df = pd.read_csv("crawler/it_jobs_vietnam.csv")
print(f"Original dataset: {len(df)} jobs\n")

# 1. Remove duplicates
print("1. Removing duplicates...")
df_clean = df.drop_duplicates(subset=['job_id'], keep='first')
print(f"   After removing duplicates: {len(df_clean)} jobs\n")

# 2. Remove jobs with missing critical fields
print("2. Removing jobs with missing critical fields...")
df_clean = df_clean.dropna(subset=['title', 'company'])
df_clean = df_clean[df_clean['title'].str.strip() != '']
df_clean = df_clean[df_clean['company'].str.strip() != '']
print(f"   After removing missing data: {len(df_clean)} jobs\n")

# 3. Clean and standardize location
print("3. Cleaning location data...")
def clean_location(loc):
    if pd.isna(loc) or loc == '':
        return 'Unknown'
    loc = str(loc).strip()
    # Standardize common city names
    if 'Hồ Chí Minh' in loc or 'HCM' in loc or 'Sài Gòn' in loc:
        return 'Hồ Chí Minh'
    elif 'Hà Nội' in loc:
        return 'Hà Nội'
    elif 'Đà Nẵng' in loc:
        return 'Đà Nẵng'
    elif 'Cần Thơ' in loc:
        return 'Cần Thơ'
    elif 'Hải Phòng' in loc:
        return 'Hải Phòng'
    return loc

df_clean['location'] = df_clean['location'].apply(clean_location)
print(f"   Location cleaned\n")

# 4. Clean skills
print("4. Cleaning skills data...")
def clean_skills(skills_str):
    if pd.isna(skills_str) or skills_str == '':
        return ''
    # Remove extra spaces and duplicates
    skills_list = [s.strip() for s in str(skills_str).split(',')]
    skills_list = [s for s in skills_list if s]  # Remove empty
    skills_list = list(dict.fromkeys(skills_list))  # Remove duplicates, keep order
    return ', '.join(skills_list)

df_clean['skills'] = df_clean['skills'].apply(clean_skills)
print(f"   Skills cleaned\n")

# 5. Clean salary data
print("5. Cleaning salary data...")
def clean_salary(val):
    if pd.isna(val) or val == '':
        return None
    try:
        return float(val)
    except:
        return None

df_clean['salary_min'] = df_clean['salary_min'].apply(clean_salary)
df_clean['salary_max'] = df_clean['salary_max'].apply(clean_salary)
print(f"   Salary cleaned\n")

# 6. Clean job title
print("6. Cleaning job titles...")
def clean_title(title):
    if pd.isna(title):
        return ''
    title = str(title).strip()
    # Remove extra spaces
    title = re.sub(r'\s+', ' ', title)
    return title

df_clean['title'] = df_clean['title'].apply(clean_title)
print(f"   Job titles cleaned\n")

# 7. Add skill count column
print("7. Adding skill count...")
df_clean['skill_count'] = df_clean['skills'].apply(
    lambda x: len([s for s in str(x).split(',') if s.strip()]) if x else 0
)
print(f"   Skill count added\n")

# 8. Filter out jobs with no skills (optional - comment out if you want to keep them)
print("8. Filtering jobs with skills...")
df_clean = df_clean[df_clean['skill_count'] > 0]
print(f"   After filtering: {len(df_clean)} jobs\n")

# 9. Reset index
df_clean = df_clean.reset_index(drop=True)

# Save cleaned data
output_file = "clean_it_jobs.csv"
df_clean.to_csv(output_file, index=False, encoding='utf-8-sig')

print("=== CLEANING SUMMARY ===")
print(f"Original jobs: {len(df)}")
print(f"Cleaned jobs: {len(df_clean)}")
print(f"Removed: {len(df) - len(df_clean)} jobs ({(len(df) - len(df_clean))/len(df)*100:.1f}%)")
print(f"\nSaved to: {output_file}")

# Display statistics
print("\n=== CLEANED DATA STATISTICS ===")
print(f"\nTop 10 locations:")
print(df_clean['location'].value_counts().head(10))

print(f"\nTop 10 companies:")
print(df_clean['company'].value_counts().head(10))

print(f"\nSkill count distribution:")
print(df_clean['skill_count'].describe())

print(f"\nJobs by search keyword:")
print(df_clean['search_keyword'].value_counts().head(10))

print("\n=== SAMPLE CLEANED DATA ===")
print(df_clean[['title', 'company', 'location', 'skill_count']].head(10))
