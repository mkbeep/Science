"""
AI/ML Trend Analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_data, save_plot, print_section

def analyze_ai_ml():
    """Analyze AI/ML trends"""
    df, conn = load_data()
    cursor = conn.cursor()
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. AI/ML skills
    ai_skills = ['AI', 'Machine Learning', 'Deep Learning', 'Data Science', 
                 'TensorFlow', 'PyTorch', 'Keras', 'NLP']
    
    cursor.execute(f"""
        SELECT skill_name, COUNT(*) as count FROM job_skills
        WHERE skill_name IN ({','.join(['?']*len(ai_skills))})
        GROUP BY skill_name ORDER BY count DESC
    """, ai_skills)
    
    data = cursor.fetchall()
    if data:
        skills, counts = zip(*data)
        colors = sns.color_palette("rocket_r", len(skills))
        axes[0, 0].barh(range(len(skills)), counts, color=colors)
        axes[0, 0].set_yticks(range(len(skills)))
        axes[0, 0].set_yticklabels(skills)
        axes[0, 0].set_title('AI/ML Skills Demand', fontweight='bold')
        axes[0, 0].invert_yaxis()
        
        for i, c in enumerate(counts):
            axes[0, 0].text(c + 0.5, i, str(c), va='center', fontweight='bold')
    
    # 2. Data skills
    data_skills = ['Data Analysis', 'Data Science', 'Big Data', 'SQL', 'Python', 'Pandas', 'NumPy']
    
    cursor.execute(f"""
        SELECT skill_name, COUNT(*) as count FROM job_skills
        WHERE skill_name IN ({','.join(['?']*len(data_skills))})
        GROUP BY skill_name ORDER BY count DESC
    """, data_skills)
    
    data = cursor.fetchall()
    if data:
        skills, counts = zip(*data)
        colors = sns.color_palette("viridis", len(skills))
        axes[0, 1].bar(range(len(skills)), counts, color=colors)
        axes[0, 1].set_xticks(range(len(skills)))
        axes[0, 1].set_xticklabels(skills, rotation=45, ha='right')
        axes[0, 1].set_title('Data Skills Demand', fontweight='bold')
        
        for i, c in enumerate(counts):
            axes[0, 1].text(i, c + 2, str(c), ha='center', fontweight='bold')
    
    # 3. AI jobs by location
    cursor.execute("""
        SELECT j.location, COUNT(DISTINCT j.job_id) as count
        FROM jobs j JOIN job_skills js ON j.job_id = js.job_id
        WHERE js.skill_name IN ('AI', 'Machine Learning', 'Deep Learning', 'Data Science')
        GROUP BY j.location ORDER BY count DESC LIMIT 10
    """)
    
    data = cursor.fetchall()
    if data:
        locs, counts = zip(*data)
        colors = sns.color_palette("coolwarm", len(locs))
        axes[1, 0].barh(range(len(locs)), counts, color=colors)
        axes[1, 0].set_yticks(range(len(locs)))
        axes[1, 0].set_yticklabels(locs)
        axes[1, 0].set_title('AI/ML Jobs by Location', fontweight='bold')
        axes[1, 0].invert_yaxis()
    
    # 4. AI jobs by level
    cursor.execute("""
        SELECT j.job_level, COUNT(DISTINCT j.job_id) as count
        FROM jobs j JOIN job_skills js ON j.job_id = js.job_id
        WHERE js.skill_name IN ('AI', 'Machine Learning', 'Deep Learning', 'Data Science')
        GROUP BY j.job_level ORDER BY count DESC
    """)
    
    data = cursor.fetchall()
    if data:
        levels, counts = zip(*data)
        colors = sns.color_palette("Set2", len(levels))
        axes[1, 1].pie(counts, labels=levels, autopct='%1.1f%%', colors=colors,
                      textprops={'fontsize': 9, 'fontweight': 'bold'})
        axes[1, 1].set_title('AI/ML Jobs by Level', fontweight='bold')
    
    fig.suptitle('AI/ML & DATA SCIENCE TRENDS', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_plot('ai_trend_analysis.png')
    
    # Stats
    cursor.execute("""
        SELECT COUNT(DISTINCT j.job_id) FROM jobs j
        JOIN job_skills js ON j.job_id = js.job_id
        WHERE js.skill_name IN ('AI', 'Machine Learning', 'Deep Learning', 'Data Science')
    """)
    ai_jobs = cursor.fetchone()[0]
    print(f"\nAI/ML Jobs: {ai_jobs} ({ai_jobs/len(df)*100:.2f}%)")
    
    conn.close()

if __name__ == "__main__":
    print_section("AI/ML TREND ANALYSIS")
    analyze_ai_ml()
    print("\n✓ Complete!")
