"""
Top Skills Analysis - Analyzes the most in-demand technical skills from IT job postings
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Skill normalization mapping
SKILL_MAPPING = {
    # Programming Languages
    'javascript': 'JavaScript', 'js': 'JavaScript', 'typescript': 'TypeScript', 'ts': 'TypeScript',
    'python': 'Python', 'java': 'Java', 'c#': 'C#', 'csharp': 'C#', 'c++': 'C++', 'cpp': 'C++',
    'php': 'PHP', 'ruby': 'Ruby', 'go': 'Go', 'golang': 'Go', 'kotlin': 'Kotlin', 'swift': 'Swift',
    'scala': 'Scala', 'rust': 'Rust',
    
    # Web Frameworks
    'react': 'React', 'reactjs': 'React', 'react.js': 'React',
    'angular': 'Angular', 'angularjs': 'Angular',
    'vue': 'Vue.js', 'vuejs': 'Vue.js', 'vue.js': 'Vue.js',
    'nodejs': 'Node.js', 'node.js': 'Node.js', 'node': 'Node.js',
    'express': 'Express.js', 'expressjs': 'Express.js',
    'django': 'Django', 'flask': 'Flask', 'spring': 'Spring',
    'spring boot': 'Spring Boot', 'springboot': 'Spring Boot',
    'asp.net': 'ASP.NET', 'aspnet': 'ASP.NET', '.net': '.NET', 'dotnet': '.NET',
    
    # Databases
    'sql': 'SQL', 'mysql': 'MySQL', 'postgresql': 'PostgreSQL', 'postgres': 'PostgreSQL',
    'mongodb': 'MongoDB', 'mongo': 'MongoDB', 'oracle': 'Oracle',
    'mssql': 'MS SQL Server', 'sql server': 'MS SQL Server',
    'redis': 'Redis', 'elasticsearch': 'Elasticsearch', 'cassandra': 'Cassandra',
    
    # Cloud & DevOps
    'aws': 'AWS', 'amazon web services': 'AWS', 'azure': 'Azure', 'microsoft azure': 'Azure',
    'gcp': 'GCP', 'google cloud': 'GCP', 'docker': 'Docker',
    'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes',
    'jenkins': 'Jenkins', 'gitlab': 'GitLab', 'github': 'GitHub', 'ci/cd': 'CI/CD',
    'terraform': 'Terraform', 'ansible': 'Ansible',
    
    # Mobile
    'android': 'Android', 'ios': 'iOS', 'react native': 'React Native',
    'flutter': 'Flutter', 'xamarin': 'Xamarin',
    
    # Data & AI
    'machine learning': 'Machine Learning', 'ml': 'Machine Learning',
    'deep learning': 'Deep Learning', 'dl': 'Deep Learning',
    'artificial intelligence': 'AI', 'ai': 'AI', 'data science': 'Data Science',
    'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch', 'keras': 'Keras',
    'pandas': 'Pandas', 'numpy': 'NumPy', 'scikit-learn': 'Scikit-learn', 'sklearn': 'Scikit-learn',
    'spark': 'Apache Spark', 'hadoop': 'Hadoop', 'kafka': 'Kafka',
    
    # Other
    'git': 'Git', 'linux': 'Linux', 'unix': 'Unix', 'html': 'HTML', 'html5': 'HTML5',
    'css': 'CSS', 'css3': 'CSS3', 'sass': 'SASS',
    'rest api': 'REST API', 'restful': 'REST API', 'graphql': 'GraphQL',
    'microservices': 'Microservices', 'agile': 'Agile', 'scrum': 'Scrum', 'jira': 'Jira',
}

# Soft skills blacklist
SOFT_SKILLS = {
    'communication', 'giao tiếp', 'teamwork', 'làm việc nhóm', 'interpersonal', 'presentation',
    'thuyết trình', 'negotiation', 'đàm phán', 'collaboration', 'hợp tác', 'english', 'tiếng anh',
    'problem solving', 'giải quyết vấn đề', 'problem-solving', 'analytical skills', 'critical thinking',
    'tư duy phân tích', 'creativity', 'sáng tạo', 'leadership', 'lãnh đạo', 'management', 'quản lý',
    'project management', 'quản lý dự án', 'time management', 'it management', 'điều hành', 'giám đốc',
    'adaptability', 'thích nghi', 'work ethic', 'attention to detail', 'organizational', 'tổ chức',
    'multitasking', 'đa nhiệm', 'self-motivated', 'proactive', 'chủ động', 'detail-oriented',
    'customer service', 'business analysis', 'phân tích kinh doanh', 'consulting', 'tư vấn',
    'training', 'đào tạo', 'mentoring', 'kinh doanh', 'business', 'tài chính', 'finance',
    'kế toán', 'accounting', 'marketing', 'digital marketing', 'sales', 'bán hàng',
    'tìm kiếm khách hàng', 'chăm sóc khách hàng', 'khách hàng', 'customer',
    'tuyển dụng', 'recruitment', 'hr', 'nhân sự', 'an toàn thông tin', 'information security',
    'tự động hóa', 'automation', 'kiểm toán', 'audit', 'vận hành', 'operations', 'logistics',
    'data analysis', 'phân tích dữ liệu', 'analysis', 'phân tích', 'reporting', 'báo cáo',
    'documentation', 'tài liệu', 'research', 'nghiên cứu', 'planning', 'strategy', 'chiến lược',
    'testing', 'kiểm thử', 'troubleshooting', 'debugging', 'gỡ lỗi', 'optimization', 'performance',
    'security', 'bảo mật', 'networking', 'mạng', 'technical support', 'hỗ trợ kỹ thuật', 'support',
    'system administration', 'administration', 'quản trị', 'database administrator', 'dba',
    'phát triển phần mềm', 'software development', 'development', 'phát triển',
    'process workflow', 'agile process', 'process management', 'information processing',
    'công nghệ thông tin', 'information technology', 'it', 'cntt', 'technology', 'công nghệ',
    'computer science', 'soft skills', 'hard skills', 'conflict resolution',
    'microsoft office', 'ms office', 'office', 'word', 'powerpoint', 'outlook', 'excel',
    'autocad', 'photoshop', 'illustrator', 'power bi', 'powerbi', 'tableau', 'sap', 'erp',
    'cloud', 'mobile', 'web', 'backend', 'frontend', 'fullstack', 'full stack', 'devops', 'software',
}

# Skill categories
CATEGORIES = {
    'Programming Languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 
                             'Ruby', 'Go', 'Kotlin', 'Swift', 'Scala', 'Rust'],
    'Web Technologies': ['React', 'Angular', 'Vue.js', 'Node.js', 'Express.js', 'Django', 'Flask',
                        'Spring', 'Spring Boot', 'ASP.NET', '.NET', 'HTML', 'HTML5', 'CSS', 'CSS3', 'SASS'],
    'Databases': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'MS SQL Server', 
                 'Redis', 'Elasticsearch', 'Cassandra'],
    'Cloud & DevOps': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 
                      'GitLab', 'GitHub', 'Terraform', 'Ansible'],
    'Mobile Development': ['Android', 'iOS', 'React Native', 'Flutter', 'Xamarin'],
    'Data & AI': ['Machine Learning', 'Deep Learning', 'AI', 'Data Science', 'TensorFlow', 
                 'PyTorch', 'Keras', 'Pandas', 'NumPy', 'Scikit-learn', 'Apache Spark', 'Hadoop', 'Kafka'],
    'Other Technologies': ['Git', 'Linux', 'Unix', 'REST API', 'GraphQL', 'Microservices', 
                          'Agile', 'Scrum', 'Jira']
}

def load_data(file_path='clean_it_jobs.csv'):
    """Load cleaned job data"""
    if not os.path.exists(file_path):
        file_path = os.path.join('..', '..', file_path)
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} job records")
    return df

def normalize_skill(skill):
    """Normalize skill name"""
    return SKILL_MAPPING.get(skill.strip().lower(), None)

def is_technical_skill(skill):
    """Check if skill is technical (not soft skill)"""
    skill_lower = skill.lower()
    # Check if any soft skill keyword is in the skill name
    return not any(soft in skill_lower for soft in SOFT_SKILLS)

def extract_all_skills(df):
    """Extract and normalize technical skills"""
    all_skills = []
    for skills_str in df['skills'].dropna():
        if isinstance(skills_str, str) and skills_str.strip():
            for skill in skills_str.split(','):
                skill = skill.strip()
                normalized = normalize_skill(skill)
                if normalized:
                    all_skills.append(normalized)
                elif is_technical_skill(skill):
                    all_skills.append(skill)
    return all_skills

def get_top_skills(all_skills, top_n=15):
    """Get top N most demanded skills"""
    return pd.DataFrame(Counter(all_skills).most_common(top_n), columns=['Skill', 'Count'])

def plot_top_skills(top_skills_df, top_n=15, save_path='analysis/topskills/'):
    """Create horizontal bar chart for top skills"""
    plt.figure(figsize=(14, 8))
    colors = sns.color_palette("viridis", len(top_skills_df))
    bars = plt.barh(range(len(top_skills_df)), top_skills_df['Count'], color=colors)
    
    plt.yticks(range(len(top_skills_df)), top_skills_df['Skill'])
    plt.xlabel('Number of Job Postings', fontsize=12, fontweight='bold')
    plt.ylabel('Skills', fontsize=12, fontweight='bold')
    plt.title(f'Top {top_n} Most In-Demand Technical Skills in Vietnam', 
              fontsize=14, fontweight='bold', pad=20)
    
    for i, (bar, count) in enumerate(zip(bars, top_skills_df['Count'])):
        plt.text(count + 1, i, str(count), va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'top_skills.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'top_skills.png')}")
    plt.show()

def analyze_skill_categories(all_skills):
    """Categorize skills into groups"""
    skill_counts = Counter(all_skills)
    categorized = {cat: 0 for cat in CATEGORIES.keys()}
    
    for skill, count in skill_counts.items():
        for category, keywords in CATEGORIES.items():
            if skill in keywords:
                categorized[category] += count
                break
    
    return categorized

def plot_skill_categories(categorized_skills, save_path='analysis/topskills/'):
    """Create pie chart for skill categories"""
    filtered_data = {k: v for k, v in categorized_skills.items() if v > 0}
    
    if not filtered_data:
        print("⚠ No categorized skills found")
        return
    
    plt.figure(figsize=(10, 8))
    colors = sns.color_palette("Set3", len(filtered_data))
    plt.pie(filtered_data.values(), labels=filtered_data.keys(), autopct='%1.1f%%',
            startangle=90, colors=colors, textprops={'fontsize': 11, 'fontweight': 'bold'})
    plt.title('Technical Skills Distribution by Category', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'skill_categories.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved: {os.path.join(save_path, 'skill_categories.png')}")
    plt.show()

def generate_report(df, top_skills_df, categorized_skills):
    """Generate text report"""
    lines = ["=" * 60, "TECHNICAL SKILLS ANALYSIS REPORT", "=" * 60, ""]
    
    total_jobs = len(df)
    jobs_with_skills = df['skills'].notna().sum()
    lines.extend([
        f"Total Job Postings: {total_jobs:,}",
        f"Jobs with Skills Listed: {jobs_with_skills:,} ({jobs_with_skills/total_jobs*100:.1f}%)",
        "", "TOP 15 MOST IN-DEMAND TECHNICAL SKILLS:", "-" * 60
    ])
    
    for idx, row in top_skills_df.head(15).iterrows():
        pct = (row['Count'] / jobs_with_skills) * 100
        lines.append(f"{idx+1:2d}. {row['Skill']:<30} {row['Count']:>5} jobs ({pct:>5.1f}%)")
    
    lines.extend(["", "TECHNICAL SKILLS BY CATEGORY:", "-" * 60])
    total_skills = sum(categorized_skills.values())
    if total_skills > 0:
        for cat, count in sorted(categorized_skills.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                pct = (count / total_skills) * 100
                lines.append(f"{cat:<25} {count:>6} ({pct:>5.1f}%)")
    
    lines.extend(["", "KEY INSIGHTS:", "-" * 60])
    if len(top_skills_df) > 0:
        top = top_skills_df.iloc[0]
        lines.append(f"• Most demanded: {top['Skill']} ({top['Count']} jobs)")
    
    if categorized_skills:
        top_cat = max(categorized_skills.items(), key=lambda x: x[1])
        if top_cat[1] > 0:
            lines.append(f"• Dominant category: {top_cat[0]} ({top_cat[1]} mentions)")
    
    lines.extend(["", "=" * 60])
    return "\n".join(lines)

def main():
    """Main execution"""
    print("Starting Technical Skills Analysis...")
    print("-" * 60)
    
    df = load_data()
    
    print("\nExtracting and normalizing technical skills...")
    all_skills = extract_all_skills(df)
    print(f"Total technical skill mentions: {len(all_skills):,}")
    print(f"Unique technical skills: {len(set(all_skills)):,}")
    
    print("\nAnalyzing top technical skills...")
    top_skills_df = get_top_skills(all_skills, top_n=15)
    
    print("\nGenerating visualizations...")
    plot_top_skills(top_skills_df, top_n=15)
    
    print("\nCategorizing technical skills...")
    categorized_skills = analyze_skill_categories(all_skills)
    plot_skill_categories(categorized_skills)
    
    print("\nGenerating report...")
    report = generate_report(df, top_skills_df, categorized_skills)
    print("\n" + report)
    
    # Save outputs
    report_path = 'analysis/topskills/skills_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✓ Report saved: {report_path}")
    
    csv_path = 'analysis/topskills/top_skills.csv'
    top_skills_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✓ Data saved: {csv_path}")
    
    print("\n" + "=" * 60)
    print("✓ Technical Skills Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
