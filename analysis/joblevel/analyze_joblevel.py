"""
Job Level Distribution Analysis - Analyzes IT jobs by experience level
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

def load_data(file_path='clean_it_jobs.csv'):
    """Load cleaned job data"""
    if not os.path.exists(file_path):
        file_path = os.path.join('..', '..', file_path)
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} job records")
    return df

def get_level_stats(df):
    """Calculate job level statistics"""
    df_level = df[df['job_level'].notna()].copy()
    level_counts = df_level['job_level'].value_counts()
    
    stats = {
        'total_jobs': len(df),
        'jobs_with_level': len(df_level),
        'percentage': len(df_level) / len(df) * 100,
        'unique_levels': df_level['job_level'].nunique(),
        'level_counts': level_counts.to_dict()
    }
    
    return stats, df_level

def plot_level_distribution(df_level, save_path='analysis/joblevel/'):
    """Create pie chart and bar chart for job level distribution"""
    level_counts = df_level['job_level'].value_counts()
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Pie chart
    colors = sns.color_palette("Set3", len(level_counts))
    wedges, texts, autotexts = axes[0].pie(
        level_counts.values,
        labels=level_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )
    axes[0].set_title('IT Job Distribution by Experience Level', fontsize=14, fontweight='bold')
    
    # Bar chart
    bars = axes[1].barh(range(len(level_counts)), level_counts.values, color=colors)
    axes[1].set_yticks(range(len(level_counts)))
    axes[1].set_yticklabels(level_counts.index)
    axes[1].set_xlabel('Number of Jobs', fontsize=12, fontweight='bold')
    axes[1].set_title('Job Count by Level', fontsize=14, fontweight='bold')
    
    for i, count in enumerate(level_counts.values):
        axes[1].text(count + 10, i, str(count), va='center', fontsize=10, fontweight='bold')
    
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'level_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'level_distribution.png')}")
    plt.show()

def plot_level_skills(df_level, save_path='analysis/joblevel/'):
    """Create chart showing top skills for each job level"""
    top_levels = df_level['job_level'].value_counts().head(5).index
    
    fig, axes = plt.subplots(len(top_levels), 1, figsize=(14, 4 * len(top_levels)))
    if len(top_levels) == 1:
        axes = [axes]
    
    for idx, level in enumerate(top_levels):
        level_jobs = df_level[df_level['job_level'] == level]
        all_skills = []
        
        for skills_str in level_jobs['skills'].dropna():
            if isinstance(skills_str, str) and skills_str.strip():
                all_skills.extend([s.strip() for s in skills_str.split(',')])
        
        if all_skills:
            top_skills = Counter(all_skills).most_common(10)
            skills, counts = zip(*top_skills)
            
            colors = sns.color_palette("viridis", len(skills))
            bars = axes[idx].barh(range(len(skills)), counts, color=colors)
            axes[idx].set_yticks(range(len(skills)))
            axes[idx].set_yticklabels(skills)
            axes[idx].set_xlabel('Mentions', fontsize=11, fontweight='bold')
            axes[idx].set_title(f'Top 10 Skills for {level} ({len(level_jobs)} jobs)', 
                               fontsize=12, fontweight='bold')
            
            for i, count in enumerate(counts):
                axes[idx].text(count + 0.5, i, str(count), va='center', fontsize=9, fontweight='bold')
            
            axes[idx].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'level_skills.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'level_skills.png')}")
    plt.show()

def plot_level_locations(df_level, save_path='analysis/joblevel/'):
    """Create stacked bar chart for job levels by location"""
    top_locations = df_level['location'].value_counts().head(5).index
    df_filtered = df_level[df_level['location'].isin(top_locations)]
    
    # Create pivot table
    pivot_data = df_filtered.groupby(['location', 'job_level']).size().unstack(fill_value=0)
    
    plt.figure(figsize=(12, 7))
    pivot_data.plot(kind='bar', stacked=True, colormap='Set3', ax=plt.gca())
    
    plt.xlabel('Location', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Jobs', fontsize=12, fontweight='bold')
    plt.title('Job Level Distribution by Top Locations', fontsize=14, fontweight='bold', pad=20)
    plt.legend(title='Job Level', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'level_by_location.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'level_by_location.png')}")
    plt.show()

def generate_report(df, stats, df_level):
    """Generate text report"""
    lines = ["=" * 60, "JOB LEVEL DISTRIBUTION ANALYSIS REPORT", "=" * 60, ""]
    
    lines.extend([
        f"Total Job Postings: {stats['total_jobs']:,}",
        f"Jobs with Level Info: {stats['jobs_with_level']:,} ({stats['percentage']:.1f}%)",
        f"Unique Job Levels: {stats['unique_levels']}",
        "", "JOB DISTRIBUTION BY LEVEL:", "-" * 60
    ])
    
    level_counts = df_level['job_level'].value_counts()
    for idx, (level, count) in enumerate(level_counts.items(), 1):
        pct = count / len(df_level) * 100
        lines.append(f"{idx}. {level:<35} {count:>5} jobs ({pct:>5.1f}%)")
    
    # Top skills by level
    lines.extend(["", "TOP 5 SKILLS BY JOB LEVEL:", "-" * 60])
    top_levels = level_counts.head(3).index
    
    for level in top_levels:
        level_jobs = df_level[df_level['job_level'] == level]
        all_skills = []
        
        for skills_str in level_jobs['skills'].dropna():
            if isinstance(skills_str, str) and skills_str.strip():
                all_skills.extend([s.strip() for s in skills_str.split(',')])
        
        if all_skills:
            top_skills = Counter(all_skills).most_common(5)
            lines.append(f"\n{level} ({len(level_jobs)} jobs):")
            for skill, count in top_skills:
                lines.append(f"  • {skill}: {count} mentions")
    
    # Location distribution
    lines.extend(["", "", "TOP 5 LOCATIONS BY JOB LEVEL:", "-" * 60])
    top_locations = df_level['location'].value_counts().head(5)
    for idx, (location, count) in enumerate(top_locations.items(), 1):
        pct = count / len(df_level) * 100
        lines.append(f"{idx}. {location:<30} {count:>5} jobs ({pct:>5.1f}%)")
    
    lines.extend(["", "KEY INSIGHTS:", "-" * 60])
    most_common = level_counts.index[0]
    lines.append(f"• Most common level: {most_common} ({level_counts.iloc[0]} jobs)")
    
    entry_levels = ['Fresher/Entry level', 'Internship', 'Student/Intern']
    entry_count = sum(level_counts.get(level, 0) for level in entry_levels)
    if entry_count > 0:
        entry_pct = entry_count / len(df_level) * 100
        lines.append(f"• Entry-level positions: {entry_count} jobs ({entry_pct:.1f}%)")
    
    senior_levels = ['Manager', 'Director and above']
    senior_count = sum(level_counts.get(level, 0) for level in senior_levels)
    if senior_count > 0:
        senior_pct = senior_count / len(df_level) * 100
        lines.append(f"• Senior positions: {senior_count} jobs ({senior_pct:.1f}%)")
    
    lines.extend(["", "=" * 60])
    return "\n".join(lines)

def main():
    """Main execution"""
    print("Starting Job Level Distribution Analysis...")
    print("-" * 60)
    
    df = load_data()
    
    print("\nCalculating job level statistics...")
    stats, df_level = get_level_stats(df)
    
    if len(df_level) == 0:
        print("⚠ No job level data available")
        return
    
    print(f"Found {len(df_level)} jobs with level information")
    
    print("\nGenerating visualizations...")
    plot_level_distribution(df_level)
    plot_level_skills(df_level)
    plot_level_locations(df_level)
    
    print("\nGenerating report...")
    report = generate_report(df, stats, df_level)
    print("\n" + report)
    
    # Save outputs
    os.makedirs('analysis/joblevel', exist_ok=True)
    
    with open('analysis/joblevel/joblevel_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✓ Report saved: analysis/joblevel/joblevel_report.txt")
    
    # Save level distribution
    level_dist = df_level['job_level'].value_counts().reset_index()
    level_dist.columns = ['Job_Level', 'Count']
    level_dist.to_csv('analysis/joblevel/level_distribution.csv', index=False, encoding='utf-8')
    print(f"✓ Data saved: analysis/joblevel/level_distribution.csv")
    
    print("\n" + "=" * 60)
    print("✓ Job Level Distribution Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
