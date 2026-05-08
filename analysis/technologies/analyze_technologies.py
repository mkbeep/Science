"""
Most Demanded Technologies Analysis - Analyzes trending technologies in IT jobs
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from itertools import combinations
import os

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Technology categories
TECH_CATEGORIES = {
    'Programming Languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Go', 'Ruby', 'Kotlin', 'Swift'],
    'Web Frameworks': ['React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring', 'ASP.NET', '.NET'],
    'Databases': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis', 'Elasticsearch'],
    'Cloud Platforms': ['AWS', 'Azure', 'GCP', 'Cloud'],
    'DevOps Tools': ['Docker', 'Kubernetes', 'Jenkins', 'GitLab', 'GitHub', 'CI/CD', 'Terraform'],
    'Mobile': ['Android', 'iOS', 'React Native', 'Flutter'],
    'AI/ML': ['Machine Learning', 'Deep Learning', 'AI', 'TensorFlow', 'PyTorch', 'Data Science'],
    'Other Tools': ['Git', 'Linux', 'Agile', 'Scrum', 'Jira', 'REST API', 'GraphQL', 'Microservices']
}

def load_data(file_path='clean_it_jobs.csv'):
    """Load cleaned job data"""
    if not os.path.exists(file_path):
        file_path = os.path.join('..', '..', file_path)
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} job records")
    return df

def categorize_tech(tech):
    """Categorize a technology"""
    tech_lower = tech.lower()
    for category, keywords in TECH_CATEGORIES.items():
        if any(kw.lower() in tech_lower or tech_lower in kw.lower() for kw in keywords):
            return category
    return None

def get_tech_categories(df):
    """Get technology distribution by category"""
    all_techs = []
    for skills_str in df['skills'].dropna():
        if isinstance(skills_str, str) and skills_str.strip():
            all_techs.extend([s.strip() for s in skills_str.split(',')])
    
    tech_counts = Counter(all_techs)
    category_counts = {cat: 0 for cat in TECH_CATEGORIES.keys()}
    categorized_techs = {cat: [] for cat in TECH_CATEGORIES.keys()}
    
    for tech, count in tech_counts.items():
        category = categorize_tech(tech)
        if category:
            category_counts[category] += count
            categorized_techs[category].append((tech, count))
    
    # Sort techs within each category
    for cat in categorized_techs:
        categorized_techs[cat] = sorted(categorized_techs[cat], key=lambda x: x[1], reverse=True)[:10]
    
    return len(all_techs), category_counts, categorized_techs

def plot_tech_categories(category_counts, save_path='analysis/technologies/'):
    """Create bar chart for technology categories"""
    filtered = {k: v for k, v in category_counts.items() if v > 0}
    if not filtered:
        print("⚠ No technology data available")
        return
    
    sorted_cats = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    categories, counts = zip(*sorted_cats)
    
    plt.figure(figsize=(12, 7))
    colors = sns.color_palette("husl", len(categories))
    bars = plt.bar(range(len(categories)), counts, color=colors)
    
    plt.xticks(range(len(categories)), categories, rotation=45, ha='right')
    plt.xlabel('Technology Category', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Mentions', fontsize=12, fontweight='bold')
    plt.title('Most Demanded Technology Categories', fontsize=14, fontweight='bold', pad=20)
    
    for i, count in enumerate(counts):
        plt.text(i, count + 5, str(count), ha='center', fontsize=10, fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'tech_categories.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'tech_categories.png')}")
    plt.show()

def plot_tech_trends(categorized_techs, save_path='analysis/technologies/'):
    """Create horizontal bar charts for top technologies in each category"""
    top_categories = ['Programming Languages', 'Web Frameworks', 'Databases', 'Cloud Platforms']
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, category in enumerate(top_categories):
        if category in categorized_techs and categorized_techs[category]:
            techs_data = categorized_techs[category][:8]
            techs, counts = zip(*techs_data)
            
            colors = sns.color_palette("viridis", len(techs))
            axes[idx].barh(range(len(techs)), counts, color=colors)
            axes[idx].set_yticks(range(len(techs)))
            axes[idx].set_yticklabels(techs)
            axes[idx].set_xlabel('Mentions', fontsize=11, fontweight='bold')
            axes[idx].set_title(f'Top {category}', fontsize=12, fontweight='bold')
            
            for i, count in enumerate(counts):
                axes[idx].text(count + 1, i, str(count), va='center', fontsize=9, fontweight='bold')
            
            axes[idx].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'tech_trends.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'tech_trends.png')}")
    plt.show()

def plot_tech_combinations(df, save_path='analysis/technologies/'):
    """Analyze common technology combinations"""
    tech_pairs = []
    
    for skills_str in df['skills'].dropna():
        if isinstance(skills_str, str) and skills_str.strip():
            techs = [s.strip() for s in skills_str.split(',')]
            known_techs = [t for t in techs if categorize_tech(t)]
            if len(known_techs) >= 2:
                tech_pairs.extend(combinations(sorted(known_techs), 2))
    
    if not tech_pairs:
        print("⚠ No technology combinations found")
        return
    
    pair_counts = Counter(tech_pairs).most_common(15)
    pairs, counts = zip(*pair_counts)
    pair_labels = [f"{p[0]} + {p[1]}" for p in pairs]
    
    plt.figure(figsize=(14, 8))
    colors = sns.color_palette("coolwarm", len(pairs))
    bars = plt.barh(range(len(pairs)), counts, color=colors)
    plt.yticks(range(len(pairs)), pair_labels)
    plt.xlabel('Co-occurrence Count', fontsize=12, fontweight='bold')
    plt.title('Top 15 Technology Combinations', fontsize=14, fontweight='bold', pad=20)
    
    for i, count in enumerate(counts):
        plt.text(count + 0.5, i, str(count), va='center', fontsize=9, fontweight='bold')
    
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'tech_combinations.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'tech_combinations.png')}")
    plt.show()

def generate_report(df, total_techs, category_counts, categorized_techs):
    """Generate text report"""
    lines = ["=" * 70, "MOST DEMANDED TECHNOLOGIES ANALYSIS REPORT", "=" * 70, ""]
    
    total_jobs = len(df)
    jobs_with_skills = df['skills'].notna().sum()
    
    lines.extend([
        f"Total Job Postings: {total_jobs:,}",
        f"Jobs with Skills: {jobs_with_skills:,} ({jobs_with_skills/total_jobs*100:.1f}%)",
        f"Total Technology Mentions: {total_techs:,}",
        "", "TECHNOLOGY CATEGORIES RANKING:", "-" * 70
    ])
    
    sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    for idx, (category, count) in enumerate(sorted_cats, 1):
        if count > 0:
            lines.append(f"{idx}. {category:<30} {count:>5} mentions")
    
    lines.extend(["", "TOP TECHNOLOGIES BY CATEGORY:", "-" * 70])
    
    for category in ['Programming Languages', 'Web Frameworks', 'Databases', 'Cloud Platforms', 'AI/ML']:
        if category in categorized_techs and categorized_techs[category]:
            lines.append(f"\n{category}:")
            for tech, count in categorized_techs[category][:5]:
                lines.append(f"  • {tech}: {count} mentions")
    
    lines.extend(["", "KEY INSIGHTS:", "-" * 70])
    
    if sorted_cats:
        top_cat = sorted_cats[0]
        lines.append(f"• Most demanded category: {top_cat[0]} ({top_cat[1]} mentions)")
    
    # Top tech overall
    all_techs = [tech for techs_list in categorized_techs.values() for tech in techs_list]
    if all_techs:
        top_tech = max(all_techs, key=lambda x: x[1])
        lines.append(f"• Most demanded technology: {top_tech[0]} ({top_tech[1]} mentions)")
    
    # Programming languages
    if 'Programming Languages' in categorized_techs and categorized_techs['Programming Languages']:
        top_lang = categorized_techs['Programming Languages'][0]
        lines.append(f"• Most popular programming language: {top_lang[0]} ({top_lang[1]} mentions)")
    
    lines.extend(["", "=" * 70])
    return "\n".join(lines)

def main():
    """Main execution"""
    print("Starting Most Demanded Technologies Analysis...")
    print("-" * 60)
    
    df = load_data()
    
    print("\nCategorizing technologies...")
    total_techs, category_counts, categorized_techs = get_tech_categories(df)
    print(f"Total technology mentions: {total_techs:,}")
    
    print("\nGenerating visualizations...")
    plot_tech_categories(category_counts)
    plot_tech_trends(categorized_techs)
    plot_tech_combinations(df)
    
    print("\nGenerating report...")
    report = generate_report(df, total_techs, category_counts, categorized_techs)
    print("\n" + report)
    
    # Save outputs
    os.makedirs('analysis/technologies', exist_ok=True)
    
    with open('analysis/technologies/technologies_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✓ Report saved: analysis/technologies/technologies_report.txt")
    
    cat_df = pd.DataFrame(sorted(category_counts.items(), key=lambda x: x[1], reverse=True),
                          columns=['Category', 'Count'])
    cat_df.to_csv('analysis/technologies/tech_categories.csv', index=False, encoding='utf-8')
    print(f"✓ Data saved: analysis/technologies/tech_categories.csv")
    
    print("\n" + "=" * 60)
    print("✓ Most Demanded Technologies Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
