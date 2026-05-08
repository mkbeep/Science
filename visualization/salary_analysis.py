"""
Salary Analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_data, save_plot, print_section

def analyze_salary():
    """Analyze salary distribution"""
    df, conn = load_data()
    
    df_salary = df[(df['salary_min'] > 0) | (df['salary_max'] > 0)].copy()
    
    if len(df_salary) == 0:
        print("⚠ No salary data available")
        conn.close()
        return
    
    df_salary['salary_m'] = ((df_salary['salary_min'] + df_salary['salary_max']) / 2) / 1_000_000
    
    print(f"Jobs with salary: {len(df_salary)} / {len(df)} ({len(df_salary)/len(df)*100:.1f}%)")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Histogram
    axes[0, 0].hist(df_salary['salary_m'], bins=30, color='#3498db', alpha=0.7, edgecolor='black')
    axes[0, 0].axvline(df_salary['salary_m'].mean(), color='red', linestyle='--', 
                      label=f'Mean: {df_salary["salary_m"].mean():.1f}M')
    axes[0, 0].axvline(df_salary['salary_m'].median(), color='green', linestyle='--',
                      label=f'Median: {df_salary["salary_m"].median():.1f}M')
    axes[0, 0].set_xlabel('Salary (Million VND)', fontweight='bold')
    axes[0, 0].set_title('Salary Distribution', fontweight='bold')
    axes[0, 0].legend()
    
    # 2. Box plot
    axes[0, 1].boxplot(df_salary['salary_m'], vert=True, patch_artist=True,
                      boxprops=dict(facecolor='#3498db', alpha=0.7))
    axes[0, 1].set_ylabel('Salary (Million VND)', fontweight='bold')
    axes[0, 1].set_title('Salary Box Plot', fontweight='bold')
    
    # 3. By job level
    level_salary = df_salary[df_salary['job_level'].notna()]
    if len(level_salary) > 0:
        level_order = level_salary.groupby('job_level')['salary_m'].median().sort_values(ascending=False).index
        sns.boxplot(data=level_salary, x='job_level', y='salary_m', order=level_order, 
                   palette='Set2', ax=axes[1, 0])
        axes[1, 0].set_xlabel('Job Level', fontweight='bold')
        axes[1, 0].set_ylabel('Salary (Million VND)', fontweight='bold')
        axes[1, 0].set_title('Salary by Level', fontweight='bold')
        axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 4. Salary ranges
    ranges = [
        ('< 10M', df_salary['salary_m'] < 10),
        ('10-20M', (df_salary['salary_m'] >= 10) & (df_salary['salary_m'] < 20)),
        ('20-30M', (df_salary['salary_m'] >= 20) & (df_salary['salary_m'] < 30)),
        ('30-50M', (df_salary['salary_m'] >= 30) & (df_salary['salary_m'] < 50)),
        ('> 50M', df_salary['salary_m'] >= 50)
    ]
    
    range_names = [r[0] for r in ranges]
    range_counts = [r[1].sum() for r in ranges]
    
    colors = sns.color_palette("RdYlGn", len(range_names))
    axes[1, 1].bar(range(len(range_names)), range_counts, color=colors, alpha=0.7, edgecolor='black')
    axes[1, 1].set_xticks(range(len(range_names)))
    axes[1, 1].set_xticklabels(range_names)
    axes[1, 1].set_ylabel('Job Count', fontweight='bold')
    axes[1, 1].set_title('Salary Ranges', fontweight='bold')
    
    for i, c in enumerate(range_counts):
        axes[1, 1].text(i, c + 1, str(c), ha='center', fontweight='bold')
    
    fig.suptitle('IT SALARY ANALYSIS', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_plot('salary_analysis.png')
    
    print(f"\nStats: Mean={df_salary['salary_m'].mean():.1f}M | Median={df_salary['salary_m'].median():.1f}M")
    conn.close()

if __name__ == "__main__":
    print_section("SALARY ANALYSIS")
    analyze_salary()
    print("\n✓ Complete!")
