"""
City Analysis - Hà Nội vs Hồ Chí Minh comparison
"""

import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_data, save_plot, print_section

def analyze_cities():
    """Compare Hà Nội vs Hồ Chí Minh"""
    df, conn = load_data()
    
    hanoi = df[df['location'] == 'Hà Nội']
    hcm = df[df['location'] == 'Hồ Chí Minh']
    
    print(f"Hà Nội: {len(hanoi)} jobs | HCM: {len(hcm)} jobs")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    cursor = conn.cursor()
    
    # 1. Job count
    cities = ['Hà Nội', 'Hồ Chí Minh']
    counts = [len(hanoi), len(hcm)]
    axes[0, 0].bar(cities, counts, color=['#FF6B6B', '#4ECDC4'], alpha=0.7, edgecolor='black')
    axes[0, 0].set_ylabel('Jobs', fontweight='bold')
    axes[0, 0].set_title('Job Count', fontweight='bold')
    for i, c in enumerate(counts):
        axes[0, 0].text(i, c + 20, str(c), ha='center', fontweight='bold')
    
    # 2. Job levels
    hanoi_levels = hanoi['job_level'].value_counts()
    hcm_levels = hcm['job_level'].value_counts()
    all_levels = list(set(hanoi_levels.index) | set(hcm_levels.index))
    
    x = range(len(all_levels))
    width = 0.35
    axes[0, 1].bar([i - width/2 for i in x], [hanoi_levels.get(l, 0) for l in all_levels], 
                   width, label='Hà Nội', color='#FF6B6B', alpha=0.7)
    axes[0, 1].bar([i + width/2 for i in x], [hcm_levels.get(l, 0) for l in all_levels],
                   width, label='HCM', color='#4ECDC4', alpha=0.7)
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels([l[:15] for l in all_levels], rotation=45, ha='right', fontsize=8)
    axes[0, 1].set_title('Job Levels', fontweight='bold')
    axes[0, 1].legend()
    
    # 3-4. Top skills
    for idx, (city, color, ax) in enumerate([
        ('Hà Nội', 'Reds_r', axes[0, 2]),
        ('Hồ Chí Minh', 'Blues_r', axes[1, 0])
    ]):
        cursor.execute("""
            SELECT js.skill_name, COUNT(*) as count
            FROM job_skills js JOIN jobs j ON js.job_id = j.job_id
            WHERE j.location = ?
            GROUP BY js.skill_name ORDER BY count DESC LIMIT 10
        """, (city,))
        skills, counts = zip(*cursor.fetchall())
        
        colors = sns.color_palette(color, len(skills))
        ax.barh(range(len(skills)), counts, color=colors)
        ax.set_yticks(range(len(skills)))
        ax.set_yticklabels(skills, fontsize=9)
        ax.set_title(f'Top Skills - {city}', fontweight='bold')
        ax.invert_yaxis()
    
    # 5-6. Top companies
    for city_df, city, color, ax in [
        (hanoi, 'Hà Nội', '#FF6B6B', axes[1, 1]),
        (hcm, 'HCM', '#4ECDC4', axes[1, 2])
    ]:
        top_companies = city_df['company'].value_counts().head(8)
        ax.barh(range(len(top_companies)), top_companies.values, color=color, alpha=0.7)
        ax.set_yticks(range(len(top_companies)))
        ax.set_yticklabels([c[:25] for c in top_companies.index], fontsize=8)
        ax.set_title(f'Top Companies - {city}', fontweight='bold')
        ax.invert_yaxis()
    
    fig.suptitle('HÀ NỘI vs HỒ CHÍ MINH COMPARISON', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_plot('city_analysis.png')
    conn.close()

if __name__ == "__main__":
    print_section("CITY ANALYSIS: HÀ NỘI vs HỒ CHÍ MINH")
    analyze_cities()
    print("\n✓ Complete!")
