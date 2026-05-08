"""
Top Companies Analysis - Analyzes top hiring companies and their requirements
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

def get_top_companies(df, top_n=15):
    """Get top N companies by job count"""
    company_counts = df['company'].value_counts().head(top_n)
    return pd.DataFrame({'Company': company_counts.index, 'Job_Count': company_counts.values})

def plot_top_companies(top_companies_df, save_path='analysis/topcompanies/'):
    """Create horizontal bar chart for top companies"""
    plt.figure(figsize=(14, 8))
    colors = sns.color_palette("rocket", len(top_companies_df))
    bars = plt.barh(range(len(top_companies_df)), top_companies_df['Job_Count'], color=colors)
    
    plt.yticks(range(len(top_companies_df)), top_companies_df['Company'])
    plt.xlabel('Number of Job Postings', fontsize=12, fontweight='bold')
    plt.ylabel('Company', fontsize=12, fontweight='bold')
    plt.title('Top 15 Companies Hiring IT Professionals', fontsize=14, fontweight='bold', pad=20)
    
    for i, count in enumerate(top_companies_df['Job_Count']):
        plt.text(count + 1, i, str(count), va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'top_companies.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'top_companies.png')}")
    plt.show()

def get_company_skills(df, company):
    """Get top skills for a specific company"""
    company_jobs = df[df['company'] == company]
    all_skills = []
    
    for skills_str in company_jobs['skills'].dropna():
        if isinstance(skills_str, str) and skills_str.strip():
            all_skills.extend([s.strip() for s in skills_str.split(',')])
    
    return Counter(all_skills).most_common(5) if all_skills else []

def plot_company_skills(df, top_n=10, save_path='analysis/topcompanies/'):
    """Create grouped bar chart showing top skills for each company"""
    top_companies = df['company'].value_counts().head(top_n).index
    
    # Collect skill data
    company_skill_data = {}
    for company in top_companies:
        top_skills = get_company_skills(df, company)
        if top_skills:
            company_skill_data[company] = {skill: count for skill, count in top_skills[:3]}
    
    if not company_skill_data:
        print("⚠ No company skills data available")
        return
    
    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(16, 10))
    companies = list(company_skill_data.keys())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    width = 0.25
    
    for idx, company in enumerate(companies):
        skills_list = list(company_skill_data[company].items())[:3]
        for skill_idx, (skill, count) in enumerate(skills_list):
            bar_pos = idx + (skill_idx - 1) * width
            ax.bar(bar_pos, count, width, color=colors[skill_idx], alpha=0.8)
            ax.text(bar_pos, count + 0.3, skill[:15], ha='center', va='bottom', 
                   fontsize=7, rotation=45, fontweight='bold')
    
    ax.set_xlabel('Company', fontsize=12, fontweight='bold')
    ax.set_ylabel('Skill Mentions', fontsize=12, fontweight='bold')
    ax.set_title('Top 3 Skills Required by Leading IT Companies', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(range(len(companies)))
    ax.set_xticklabels([c[:30] + '...' if len(c) > 30 else c for c in companies], 
                       rotation=45, ha='right', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'company_skills.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'company_skills.png')}")
    plt.show()

def get_company_skills_report(df, top_n=10):
    """Get company skills data for report"""
    top_companies = df['company'].value_counts().head(top_n).index
    company_skills = []
    
    for company in top_companies:
        company_jobs = df[df['company'] == company]
        top_skills = get_company_skills(df, company)
        
        if top_skills:
            skills_text = ', '.join([f"{skill} ({count})" for skill, count in top_skills])
            company_skills.append({
                'Company': company,
                'Job_Count': len(company_jobs),
                'Top_Skills': skills_text
            })
    
    return pd.DataFrame(company_skills)

def get_company_salary(df, top_n=10):
    """Analyze average salary by top companies"""
    df_salary = df[(df['salary_min'] > 0) | (df['salary_max'] > 0)].copy()
    df_salary['avg_salary'] = (df_salary['salary_min'] + df_salary['salary_max']) / 2
    
    company_salary = df_salary.groupby('company').agg({
        'avg_salary': 'mean',
        'job_id': 'count'
    }).reset_index()
    company_salary.columns = ['Company', 'Avg_Salary', 'Job_Count']
    
    return company_salary[company_salary['Job_Count'] >= 3].sort_values('Avg_Salary', ascending=False).head(top_n)

def plot_company_salary(company_salary_df, save_path='analysis/topcompanies/'):
    """Create bar chart for average salary by company"""
    if len(company_salary_df) == 0:
        print("⚠ No salary data available")
        return
    
    plt.figure(figsize=(14, 8))
    colors = sns.color_palette("mako", len(company_salary_df))
    salaries_m = company_salary_df['Avg_Salary'] / 1_000_000
    bars = plt.barh(range(len(company_salary_df)), salaries_m, color=colors)
    
    plt.yticks(range(len(company_salary_df)), company_salary_df['Company'])
    plt.xlabel('Average Salary (Million VND)', fontsize=12, fontweight='bold')
    plt.ylabel('Company', fontsize=12, fontweight='bold')
    plt.title('Top Companies by Average Salary', fontsize=14, fontweight='bold', pad=20)
    
    for i, salary in enumerate(salaries_m):
        plt.text(salary + 0.5, i, f'{salary:.1f}M', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'company_salary.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'company_salary.png')}")
    plt.show()

def generate_report(df, top_companies_df, company_skills_df, company_salary_df):
    """Generate text report"""
    lines = ["=" * 70, "TOP COMPANIES ANALYSIS REPORT", "=" * 70, ""]
    
    total_jobs = len(df)
    total_companies = df['company'].nunique()
    
    lines.extend([
        f"Total Job Postings: {total_jobs:,}",
        f"Total Unique Companies: {total_companies:,}",
        "", "TOP 15 COMPANIES BY JOB COUNT:", "-" * 70
    ])
    
    for idx, row in top_companies_df.iterrows():
        pct = (row['Job_Count'] / total_jobs) * 100
        lines.append(f"{idx+1:2d}. {row['Company']:<45} {row['Job_Count']:>4} jobs ({pct:>4.1f}%)")
    
    if len(company_skills_df) > 0:
        lines.extend(["", "TOP SKILLS REQUIRED BY LEADING COMPANIES:", "-" * 70])
        for idx, row in company_skills_df.iterrows():
            lines.append(f"\n{idx+1}. {row['Company']} ({row['Job_Count']} jobs)")
            lines.append(f"   Top Skills: {row['Top_Skills']}")
    
    if len(company_salary_df) > 0:
        lines.extend(["", "", "TOP COMPANIES BY AVERAGE SALARY:", "-" * 70])
        for idx, row in company_salary_df.iterrows():
            lines.append(f"{idx+1:2d}. {row['Company']:<45} {row['Avg_Salary']/1_000_000:>6.1f}M VND "
                        f"({row['Job_Count']} jobs)")
    
    lines.extend(["", "KEY INSIGHTS:", "-" * 70])
    top = top_companies_df.iloc[0]
    lines.append(f"• Most active recruiter: {top['Company']} ({top['Job_Count']} jobs)")
    
    if len(company_salary_df) > 0:
        top_salary = company_salary_df.iloc[0]
        lines.append(f"• Highest paying company: {top_salary['Company']} "
                    f"({top_salary['Avg_Salary']/1_000_000:.1f}M VND)")
    
    top5_pct = (top_companies_df.head(5)['Job_Count'].sum() / total_jobs) * 100
    lines.append(f"• Top 5 companies account for {top5_pct:.1f}% of all job postings")
    
    lines.extend(["", "=" * 70])
    return "\n".join(lines)

def main():
    """Main execution"""
    print("Starting Top Companies Analysis...")
    print("-" * 60)
    
    df = load_data()
    
    print("\nAnalyzing top companies...")
    top_companies_df = get_top_companies(df, top_n=15)
    
    print("\nGenerating visualizations...")
    plot_top_companies(top_companies_df)
    
    print("\nAnalyzing company skill requirements...")
    plot_company_skills(df, top_n=10)
    
    print("\nAnalyzing company salaries...")
    company_salary_df = get_company_salary(df, top_n=10)
    plot_company_salary(company_salary_df)
    
    print("\nGenerating report...")
    company_skills_df = get_company_skills_report(df, top_n=10)
    report = generate_report(df, top_companies_df, company_skills_df, company_salary_df)
    print("\n" + report)
    
    # Save outputs
    os.makedirs('analysis/topcompanies', exist_ok=True)
    
    with open('analysis/topcompanies/companies_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✓ Report saved: analysis/topcompanies/companies_report.txt")
    
    top_companies_df.to_csv('analysis/topcompanies/top_companies.csv', index=False, encoding='utf-8')
    print(f"✓ Data saved: analysis/topcompanies/top_companies.csv")
    
    if len(company_skills_df) > 0:
        company_skills_df.to_csv('analysis/topcompanies/company_skills.csv', index=False, encoding='utf-8')
        print(f"✓ Skills data saved: analysis/topcompanies/company_skills.csv")
    
    if len(company_salary_df) > 0:
        company_salary_df.to_csv('analysis/topcompanies/company_salary.csv', index=False, encoding='utf-8')
        print(f"✓ Salary data saved: analysis/topcompanies/company_salary.csv")
    
    print("\n" + "=" * 60)
    print("✓ Top Companies Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
