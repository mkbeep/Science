"""
PHASE 6: COMPREHENSIVE DASHBOARD
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from datetime import datetime
from utils import save_plot, print_section
import os

def create_dashboard():
    """Create comprehensive dashboard"""
    df = pd.read_csv('clean_it_jobs.csv')
    conn = sqlite3.connect('it_jobs_vietnam.db')
    cursor = conn.cursor()
    
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Job levels (Pie)
    ax1 = fig.add_subplot(gs[0, 0])
    level_counts = df['job_level'].value_counts()
    ax1.pie(level_counts.values, labels=level_counts.index, autopct='%1.1f%%',
            colors=sns.color_palette("Set3", len(level_counts)), textprops={'fontsize': 8})
    ax1.set_title('Job Levels', fontweight='bold')
    
    # 2. Top locations (Bar)
    ax2 = fig.add_subplot(gs[0, 1])
    top_locs = df['location'].value_counts().head(10)
    ax2.barh(range(len(top_locs)), top_locs.values, color='skyblue')
    ax2.set_yticks(range(len(top_locs)))
    ax2.set_yticklabels(top_locs.index, fontsize=8)
    ax2.set_title('Top 10 Locations', fontweight='bold')
    ax2.invert_yaxis()
    
    # 3. Top companies (Bar)
    ax3 = fig.add_subplot(gs[0, 2])
    top_companies = df['company'].value_counts().head(10)
    ax3.barh(range(len(top_companies)), top_companies.values, color='lightcoral')
    ax3.set_yticks(range(len(top_companies)))
    ax3.set_yticklabels([c[:25] for c in top_companies.index], fontsize=8)
    ax3.set_title('Top 10 Companies', fontweight='bold')
    ax3.invert_yaxis()
    
    # 4. Top skills (Bar)
    ax4 = fig.add_subplot(gs[1, :])
    cursor.execute("""
        SELECT skill_name, COUNT(*) as count FROM job_skills
        GROUP BY skill_name ORDER BY count DESC LIMIT 15
    """)
    skills, counts = zip(*cursor.fetchall())
    
    colors = sns.color_palette("viridis", len(skills))
    ax4.bar(range(len(skills)), counts, color=colors)
    ax4.set_xticks(range(len(skills)))
    ax4.set_xticklabels(skills, rotation=45, ha='right', fontsize=9)
    ax4.set_title('Top 15 Skills', fontweight='bold', fontsize=12)
    
    for i, c in enumerate(counts):
        ax4.text(i, c + 5, str(c), ha='center', fontsize=8, fontweight='bold')
    
    # 5. Skills distribution (Histogram)
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.hist(df['skill_count'], bins=20, color='mediumpurple', alpha=0.7, edgecolor='black')
    ax5.axvline(df['skill_count'].mean(), color='red', linestyle='--', 
               label=f'Mean: {df["skill_count"].mean():.1f}')
    ax5.set_title('Skills per Job', fontweight='bold')
    ax5.legend(fontsize=8)
    
    # 6. Location concentration (Pie)
    ax6 = fig.add_subplot(gs[2, 1])
    top2 = df['location'].value_counts().head(2)
    pie_data = list(top2.values) + [len(df) - top2.sum()]
    pie_labels = list(top2.index) + ['Others']
    ax6.pie(pie_data, labels=pie_labels, autopct='%1.1f%%',
            colors=['#ff9999', '#66b3ff', '#99ff99'], textprops={'fontsize': 9})
    ax6.set_title('Location Concentration', fontweight='bold')
    
    # 7. Statistics (Text)
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.axis('off')
    
    stats = f"""KEY STATISTICS
{'='*25}

Total Jobs: {len(df):,}
Companies: {df['company'].nunique():,}
Locations: {df['location'].nunique()}

Avg Skills/Job: {df['skill_count'].mean():.1f}

Top Location: {df['location'].value_counts().index[0]}
Top Skill: {skills[0]}
"""
    
    ax7.text(0.1, 0.9, stats, transform=ax7.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    fig.suptitle('IT JOBS VIETNAM - COMPREHENSIVE DASHBOARD', fontsize=16, fontweight='bold')
    save_plot('comprehensive_dashboard.png')
    conn.close()

def create_tech_trends():
    """Create technology trends"""
    conn = sqlite3.connect('it_jobs_vietnam.db')
    cursor = conn.cursor()
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    tech_categories = [
        (['Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Go', 'Ruby'], 'Programming Languages', 'rocket'),
        (['React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring'], 'Web Frameworks', 'mako'),
        (['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis'], 'Databases', 'viridis'),
        (['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins'], 'Cloud & DevOps', 'coolwarm')
    ]
    
    for idx, (techs, title, palette) in enumerate(tech_categories):
        ax = axes[idx // 2, idx % 2]
        
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            WHERE skill_name IN ({','.join(['?']*len(techs))})
            GROUP BY skill_name ORDER BY count DESC
        """, techs)
        
        data = cursor.fetchall()
        if data:
            skills, counts = zip(*data)
            colors = sns.color_palette(palette, len(skills))
            
            if idx % 2 == 0:  # Horizontal
                ax.barh(range(len(skills)), counts, color=colors)
                ax.set_yticks(range(len(skills)))
                ax.set_yticklabels(skills)
                ax.invert_yaxis()
            else:  # Vertical
                ax.bar(range(len(skills)), counts, color=colors)
                ax.set_xticks(range(len(skills)))
                ax.set_xticklabels(skills, rotation=45, ha='right')
            
            ax.set_title(title, fontweight='bold')
    
    fig.suptitle('TECHNOLOGY TRENDS', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_plot('technology_trends.png')
    conn.close()

def generate_report():
    """Generate final report"""
    df = pd.read_csv('clean_it_jobs.csv')
    conn = sqlite3.connect('it_jobs_vietnam.db')
    cursor = conn.cursor()
    
    lines = ["="*80, "IT JOBS VIETNAM - FINAL REPORT", 
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "="*80, ""]
    
    # Overview
    lines.extend([
        "1. OVERVIEW", "-"*80,
        f"Total Jobs: {len(df):,}",
        f"Companies: {df['company'].nunique():,}",
        f"Locations: {df['location'].nunique()}",
        ""
    ])
    
    # Top locations
    lines.extend(["2. TOP 10 LOCATIONS", "-"*80])
    for idx, (loc, count) in enumerate(df['location'].value_counts().head(10).items(), 1):
        lines.append(f"  {idx:2d}. {loc:<30} {count:>5} jobs")
    lines.append("")
    
    # Top skills
    lines.extend(["3. TOP 15 SKILLS", "-"*80])
    cursor.execute("SELECT skill_name, COUNT(*) FROM job_skills GROUP BY skill_name ORDER BY COUNT(*) DESC LIMIT 15")
    for idx, (skill, count) in enumerate(cursor.fetchall(), 1):
        lines.append(f"  {idx:2d}. {skill:<40} {count:>5} mentions")
    
    lines.extend(["", "="*80])
    
    report = "\n".join(lines)
    
    os.makedirs('visualization', exist_ok=True)
    with open('visualization/final_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✓ Report saved: visualization/final_report.txt")
    conn.close()
    return report

def main():
    """Main execution"""
    print_section("PHASE 6: COMPREHENSIVE VISUALIZATION")
    
    print("\n[1] Creating dashboard...")
    create_dashboard()
    
    print("\n[2] Creating technology trends...")
    create_tech_trends()
    
    print("\n[3] Generating report...")
    report = generate_report()
    print("\n" + report)
    
    print("\n✓ Phase 6 complete!")

if __name__ == "__main__":
    main()
