"""
Top Locations Analysis - Analyzes job distribution and salary by location
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Location normalization mapping
LOCATION_MAPPING = {
    'hà nội': 'Hà Nội', 'ha noi': 'Hà Nội', 'hanoi': 'Hà Nội',
    'hồ chí minh': 'Hồ Chí Minh', 'ho chi minh': 'Hồ Chí Minh', 'hcm': 'Hồ Chí Minh',
    'tp hcm': 'Hồ Chí Minh', 'tp.hcm': 'Hồ Chí Minh', 'sài gòn': 'Hồ Chí Minh', 'saigon': 'Hồ Chí Minh',
    'đà nẵng': 'Đà Nẵng', 'da nang': 'Đà Nẵng', 'danang': 'Đà Nẵng',
    'cần thơ': 'Cần Thơ', 'can tho': 'Cần Thơ',
    'hải phòng': 'Hải Phòng', 'hai phong': 'Hải Phòng',
    'bình dương': 'Bình Dương', 'binh duong': 'Bình Dương',
    'đồng nai': 'Đồng Nai', 'dong nai': 'Đồng Nai',
}

def load_data(file_path='clean_it_jobs.csv'):
    """Load cleaned job data"""
    if not os.path.exists(file_path):
        file_path = os.path.join('..', '..', file_path)
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} job records")
    return df

def normalize_location(location):
    """Normalize location name"""
    if pd.isna(location):
        return None
    return LOCATION_MAPPING.get(location.strip().lower(), location.strip())

def get_top_locations(df, top_n=10):
    """Get top N locations by job count"""
    locations = [normalize_location(loc) for loc in df['location'].dropna()]
    return pd.DataFrame(Counter(locations).most_common(top_n), columns=['Location', 'Job_Count'])

def plot_top_locations(top_locations_df, save_path='analysis/toplocations/'):
    """Create bar chart for top locations"""
    plt.figure(figsize=(12, 7))
    colors = sns.color_palette("coolwarm", len(top_locations_df))
    bars = plt.bar(range(len(top_locations_df)), top_locations_df['Job_Count'], color=colors)
    
    plt.xticks(range(len(top_locations_df)), top_locations_df['Location'], rotation=45, ha='right')
    plt.xlabel('Location', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
    plt.title('Top Locations for IT Jobs in Vietnam', fontsize=14, fontweight='bold', pad=20)
    
    for i, count in enumerate(top_locations_df['Job_Count']):
        plt.text(i, count + 10, str(count), ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'top_locations.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'top_locations.png')}")
    plt.show()

def get_location_salary(df):
    """Analyze average salary by location"""
    df_salary = df[(df['salary_min'] > 0) | (df['salary_max'] > 0)].copy()
    df_salary['location_normalized'] = df_salary['location'].apply(normalize_location)
    df_salary['avg_salary'] = (df_salary['salary_min'] + df_salary['salary_max']) / 2
    
    location_salary = df_salary.groupby('location_normalized').agg({
        'avg_salary': 'mean',
        'job_id': 'count'
    }).reset_index()
    location_salary.columns = ['Location', 'Avg_Salary', 'Job_Count']
    
    return location_salary[location_salary['Job_Count'] >= 5].sort_values('Avg_Salary', ascending=False).head(10)

def plot_location_salary(location_salary_df, save_path='analysis/toplocations/'):
    """Create bar chart for average salary by location"""
    if len(location_salary_df) == 0:
        print("⚠ No salary data available")
        return
    
    plt.figure(figsize=(12, 7))
    colors = sns.color_palette("viridis", len(location_salary_df))
    salaries_m = location_salary_df['Avg_Salary'] / 1_000_000
    bars = plt.bar(range(len(location_salary_df)), salaries_m, color=colors)
    
    plt.xticks(range(len(location_salary_df)), location_salary_df['Location'], rotation=45, ha='right')
    plt.xlabel('Location', fontsize=12, fontweight='bold')
    plt.ylabel('Average Salary (Million VND)', fontsize=12, fontweight='bold')
    plt.title('Average IT Salary by Location', fontsize=14, fontweight='bold', pad=20)
    
    for i, salary in enumerate(salaries_m):
        plt.text(i, salary + 0.5, f'{salary:.1f}M', ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'location_salary.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'location_salary.png')}")
    plt.show()

def generate_report(df, top_locations_df, location_salary_df):
    """Generate text report"""
    lines = ["=" * 60, "TOP LOCATIONS ANALYSIS REPORT", "=" * 60, ""]
    
    total_jobs = len(df)
    jobs_with_location = df['location'].notna().sum()
    
    lines.extend([
        f"Total Job Postings: {total_jobs:,}",
        f"Jobs with Location: {jobs_with_location:,} ({jobs_with_location/total_jobs*100:.1f}%)",
        "", "TOP 10 LOCATIONS BY JOB COUNT:", "-" * 60
    ])
    
    for idx, row in top_locations_df.iterrows():
        pct = (row['Job_Count'] / jobs_with_location) * 100
        lines.append(f"{idx+1:2d}. {row['Location']:<25} {row['Job_Count']:>5} jobs ({pct:>5.1f}%)")
    
    if len(location_salary_df) > 0:
        lines.extend(["", "TOP LOCATIONS BY AVERAGE SALARY:", "-" * 60])
        for idx, row in location_salary_df.iterrows():
            lines.append(f"{idx+1:2d}. {row['Location']:<25} {row['Avg_Salary']/1_000_000:>6.1f}M VND "
                        f"({row['Job_Count']} jobs)")
    
    lines.extend(["", "KEY INSIGHTS:", "-" * 60])
    top = top_locations_df.iloc[0]
    lines.append(f"• Most jobs: {top['Location']} ({top['Job_Count']} jobs)")
    
    if len(location_salary_df) > 0:
        top_salary = location_salary_df.iloc[0]
        lines.append(f"• Highest avg salary: {top_salary['Location']} "
                    f"({top_salary['Avg_Salary']/1_000_000:.1f}M VND)")
    
    if len(top_locations_df) >= 2:
        top2_pct = (top_locations_df.head(2)['Job_Count'].sum() / jobs_with_location) * 100
        lines.append(f"• Top 2 cities concentrate {top2_pct:.1f}% of all jobs")
    
    lines.extend(["", "=" * 60])
    return "\n".join(lines)

def main():
    """Main execution"""
    print("Starting Top Locations Analysis...")
    print("-" * 60)
    
    df = load_data()
    
    print("\nAnalyzing top locations...")
    top_locations_df = get_top_locations(df, top_n=10)
    print(f"Unique locations: {df['location'].nunique()}")
    
    print("\nGenerating visualizations...")
    plot_top_locations(top_locations_df)
    
    print("\nAnalyzing salary by location...")
    location_salary_df = get_location_salary(df)
    plot_location_salary(location_salary_df)
    
    print("\nGenerating report...")
    report = generate_report(df, top_locations_df, location_salary_df)
    print("\n" + report)
    
    # Save outputs
    os.makedirs('analysis/toplocations', exist_ok=True)
    
    with open('analysis/toplocations/locations_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✓ Report saved: analysis/toplocations/locations_report.txt")
    
    top_locations_df.to_csv('analysis/toplocations/top_locations.csv', index=False, encoding='utf-8')
    print(f"✓ Data saved: analysis/toplocations/top_locations.csv")
    
    if len(location_salary_df) > 0:
        location_salary_df.to_csv('analysis/toplocations/location_salary.csv', index=False, encoding='utf-8')
        print(f"✓ Salary data saved: analysis/toplocations/location_salary.csv")
    
    print("\n" + "=" * 60)
    print("✓ Top Locations Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
