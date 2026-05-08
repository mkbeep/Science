"""
IT JOBS VIETNAM - INTERACTIVE DASHBOARD
Streamlit web application for data visualization and job search
"""

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Page config
st.set_page_config(
    page_title="IT Jobs Vietnam Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load data from CSV and database"""
    df = pd.read_csv('clean_it_jobs.csv')
    return df

@st.cache_resource
def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('it_jobs_vietnam.db', check_same_thread=False)

# Initialize
df = load_data()
conn = get_db_connection()

# Sidebar
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio(
    "Select Page:",
    ["🏠 Overview", "📊 Analytics", "🔎 Job Search", "📈 Trends", "ℹ️ About"]
)

# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================
if page == "🏠 Overview":
    st.markdown('<div class="main-header">💼 IT JOBS VIETNAM DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", f"{len(df):,}")
    with col2:
        st.metric("Companies", f"{df['company'].nunique():,}")
    with col3:
        st.metric("Locations", df['location'].nunique())
    with col4:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT skill_name) FROM job_skills")
        st.metric("Unique Skills", f"{cursor.fetchone()[0]:,}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Top 10 Locations")
        top_locs = df['location'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(range(len(top_locs)), top_locs.values, color='skyblue')
        ax.set_yticks(range(len(top_locs)))
        ax.set_yticklabels(top_locs.index)
        ax.set_xlabel('Job Count')
        ax.invert_yaxis()
        st.pyplot(fig)
    
    with col2:
        st.subheader("💼 Job Level Distribution")
        level_counts = df['job_level'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(level_counts.values, labels=level_counts.index, autopct='%1.1f%%',
               colors=sns.color_palette("Set3", len(level_counts)))
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Top skills
    st.subheader("🔥 Top 15 Most In-Demand Skills")
    cursor.execute("""
        SELECT skill_name, COUNT(*) as count
        FROM job_skills
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 15
    """)
    skills_data = cursor.fetchall()
    skills_df = pd.DataFrame(skills_data, columns=['Skill', 'Count'])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("viridis", len(skills_df))
    ax.bar(range(len(skills_df)), skills_df['Count'], color=colors)
    ax.set_xticks(range(len(skills_df)))
    ax.set_xticklabels(skills_df['Skill'], rotation=45, ha='right')
    ax.set_ylabel('Demand Count')
    ax.set_title('Top 15 Skills')
    st.pyplot(fig)

# ============================================================================
# PAGE 2: ANALYTICS
# ============================================================================
elif page == "📊 Analytics":
    st.title("📊 Data Analytics")
    
    tab1, tab2, tab3 = st.tabs(["🏙️ Cities", "🤖 AI/ML", "🏢 Companies"])
    
    # Tab 1: Cities
    with tab1:
        st.subheader("Hà Nội vs Hồ Chí Minh Comparison")
        
        hanoi = df[df['location'] == 'Hà Nội']
        hcm = df[df['location'] == 'Hồ Chí Minh']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Hà Nội Jobs", len(hanoi))
        with col2:
            st.metric("HCM Jobs", len(hcm))
        
        # Job count comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        cities = ['Hà Nội', 'Hồ Chí Minh']
        counts = [len(hanoi), len(hcm)]
        ax.bar(cities, counts, color=['#FF6B6B', '#4ECDC4'], alpha=0.7)
        ax.set_ylabel('Job Count')
        ax.set_title('Job Count Comparison')
        for i, c in enumerate(counts):
            ax.text(i, c + 20, str(c), ha='center', fontweight='bold')
        st.pyplot(fig)
        
        # Top skills comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top Skills in Hà Nội**")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT js.skill_name, COUNT(*) as count
                FROM job_skills js JOIN jobs j ON js.job_id = j.job_id
                WHERE j.location = 'Hà Nội'
                GROUP BY js.skill_name ORDER BY count DESC LIMIT 10
            """)
            hn_skills = pd.DataFrame(cursor.fetchall(), columns=['Skill', 'Count'])
            st.dataframe(hn_skills, use_container_width=True)
        
        with col2:
            st.write("**Top Skills in HCM**")
            cursor.execute("""
                SELECT js.skill_name, COUNT(*) as count
                FROM job_skills js JOIN jobs j ON js.job_id = j.job_id
                WHERE j.location = 'Hồ Chí Minh'
                GROUP BY js.skill_name ORDER BY count DESC LIMIT 10
            """)
            hcm_skills = pd.DataFrame(cursor.fetchall(), columns=['Skill', 'Count'])
            st.dataframe(hcm_skills, use_container_width=True)
    
    # Tab 2: AI/ML
    with tab2:
        st.subheader("🤖 AI/ML Trend Analysis")
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT j.job_id)
            FROM jobs j JOIN job_skills js ON j.job_id = js.job_id
            WHERE js.skill_name IN ('AI', 'Machine Learning', 'Deep Learning', 'Data Science')
        """)
        ai_jobs = cursor.fetchone()[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("AI/ML Jobs", ai_jobs)
        with col2:
            st.metric("Percentage", f"{ai_jobs/len(df)*100:.2f}%")
        with col3:
            st.metric("Total Jobs", len(df))
        
        # AI/ML skills
        ai_skills = ['AI', 'Machine Learning', 'Deep Learning', 'Data Science', 
                     'TensorFlow', 'PyTorch', 'Keras']
        
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            WHERE skill_name IN ({','.join(['?']*len(ai_skills))})
            GROUP BY skill_name ORDER BY count DESC
        """, ai_skills)
        
        ai_data = cursor.fetchall()
        if ai_data:
            ai_df = pd.DataFrame(ai_data, columns=['Skill', 'Count'])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = sns.color_palette("rocket_r", len(ai_df))
            ax.barh(range(len(ai_df)), ai_df['Count'], color=colors)
            ax.set_yticks(range(len(ai_df)))
            ax.set_yticklabels(ai_df['Skill'])
            ax.set_xlabel('Job Mentions')
            ax.set_title('AI/ML Skills Demand')
            ax.invert_yaxis()
            st.pyplot(fig)
    
    # Tab 3: Companies
    with tab3:
        st.subheader("🏢 Top Companies Analysis")
        
        top_companies = df['company'].value_counts().head(15)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.barh(range(len(top_companies)), top_companies.values, color='lightcoral')
        ax.set_yticks(range(len(top_companies)))
        ax.set_yticklabels([c[:40] for c in top_companies.index])
        ax.set_xlabel('Job Count')
        ax.set_title('Top 15 Companies')
        ax.invert_yaxis()
        st.pyplot(fig)
        
        # Company details
        st.write("**Company Details**")
        companies_df = pd.DataFrame({
            'Company': top_companies.index,
            'Job Count': top_companies.values,
            'Percentage': (top_companies.values / len(df) * 100).round(2)
        })
        st.dataframe(companies_df, use_container_width=True)

# ============================================================================
# PAGE 3: JOB SEARCH
# ============================================================================
elif page == "🔎 Job Search":
    st.title("🔎 Job Search")
    
    # Search filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_skill = st.text_input("🔍 Search by Skill", placeholder="e.g., Python, Java")
    
    with col2:
        locations = ['All'] + sorted(df['location'].unique().tolist())
        search_location = st.selectbox("📍 Location", locations)
    
    with col3:
        levels = ['All'] + sorted(df['job_level'].unique().tolist())
        search_level = st.selectbox("💼 Job Level", levels)
    
    # Filter data
    filtered_df = df.copy()
    
    if search_skill:
        filtered_df = filtered_df[filtered_df['skills'].str.contains(search_skill, case=False, na=False)]
    
    if search_location != 'All':
        filtered_df = filtered_df[filtered_df['location'] == search_location]
    
    if search_level != 'All':
        filtered_df = filtered_df[filtered_df['job_level'] == search_level]
    
    # Results
    st.markdown(f"### Found {len(filtered_df)} jobs")
    
    if len(filtered_df) > 0:
        # Display results
        for idx, row in filtered_df.head(20).iterrows():
            with st.expander(f"**{row['title']}** - {row['company']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Company:** {row['company']}")
                    st.write(f"**Location:** {row['location']}")
                    st.write(f"**Level:** {row['job_level']}")
                with col2:
                    if pd.notna(row['skills']):
                        st.write(f"**Skills:** {row['skills']}")
                    st.write(f"**Job ID:** {row['job_id']}")
    else:
        st.info("No jobs found matching your criteria.")

# ============================================================================
# PAGE 4: TRENDS
# ============================================================================
elif page == "📈 Trends":
    st.title("📈 Technology Trends")
    
    cursor = conn.cursor()
    
    # Technology categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💻 Programming Languages")
        prog_langs = ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Go']
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            WHERE skill_name IN ({','.join(['?']*len(prog_langs))})
            GROUP BY skill_name ORDER BY count DESC
        """, prog_langs)
        
        lang_data = cursor.fetchall()
        if lang_data:
            lang_df = pd.DataFrame(lang_data, columns=['Language', 'Count'])
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = sns.color_palette("rocket", len(lang_df))
            ax.barh(range(len(lang_df)), lang_df['Count'], color=colors)
            ax.set_yticks(range(len(lang_df)))
            ax.set_yticklabels(lang_df['Language'])
            ax.invert_yaxis()
            st.pyplot(fig)
    
    with col2:
        st.subheader("🗄️ Databases")
        databases = ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis']
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            WHERE skill_name IN ({','.join(['?']*len(databases))})
            GROUP BY skill_name ORDER BY count DESC
        """, databases)
        
        db_data = cursor.fetchall()
        if db_data:
            db_df = pd.DataFrame(db_data, columns=['Database', 'Count'])
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = sns.color_palette("viridis", len(db_df))
            ax.barh(range(len(db_df)), db_df['Count'], color=colors)
            ax.set_yticks(range(len(db_df)))
            ax.set_yticklabels(db_df['Database'])
            ax.invert_yaxis()
            st.pyplot(fig)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌐 Web Frameworks")
        frameworks = ['React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask']
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            WHERE skill_name IN ({','.join(['?']*len(frameworks))})
            GROUP BY skill_name ORDER BY count DESC
        """, frameworks)
        
        fw_data = cursor.fetchall()
        if fw_data:
            fw_df = pd.DataFrame(fw_data, columns=['Framework', 'Count'])
            st.dataframe(fw_df, use_container_width=True)
    
    with col2:
        st.subheader("☁️ Cloud & DevOps")
        cloud = ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins']
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            WHERE skill_name IN ({','.join(['?']*len(cloud))})
            GROUP BY skill_name ORDER BY count DESC
        """, cloud)
        
        cloud_data = cursor.fetchall()
        if cloud_data:
            cloud_df = pd.DataFrame(cloud_data, columns=['Technology', 'Count'])
            st.dataframe(cloud_df, use_container_width=True)

# ============================================================================
# PAGE 5: ABOUT
# ============================================================================
elif page == "ℹ️ About":
    st.title("ℹ️ About This Project")
    
    st.markdown("""
    ## 💼 IT Jobs Vietnam Dashboard
    
    **Interactive web application for IT job market analysis in Vietnam**
    
    ### 📊 Features:
    - **Overview Dashboard**: Key metrics and visualizations
    - **Data Analytics**: Deep dive into cities, AI/ML trends, and companies
    - **Job Search**: Interactive search with filters
    - **Technology Trends**: Analysis of programming languages, databases, frameworks
    
    ### 🔧 Technology Stack:
    - **Data Collection**: VietnamWorks API
    - **Data Processing**: Python, Pandas
    - **Database**: SQLite
    - **Visualization**: Matplotlib, Seaborn
    - **Web Framework**: Streamlit
    
    ### 📈 Dataset:
    - **Total Jobs**: {total_jobs:,}
    - **Companies**: {companies:,}
    - **Locations**: {locations}
    - **Skills**: {skills:,}
    
    ### 👨‍💻 Project Pipeline:
    1. **Phase 1**: Data crawling from VietnamWorks API
    2. **Phase 2**: Data cleaning and preprocessing
    3. **Phase 3**: Database storage (SQLite)
    4. **Phase 4**: SQL search queries
    5. **Phase 5**: Data analysis and visualization
    6. **Phase 6**: Interactive Streamlit dashboard
    
    ---
    
    **Built with ❤️ for IT job market analysis**
    """.format(
        total_jobs=len(df),
        companies=df['company'].nunique(),
        locations=df['location'].nunique(),
        skills=conn.cursor().execute("SELECT COUNT(DISTINCT skill_name) FROM job_skills").fetchone()[0]
    ))

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"📊 Dataset: {len(df):,} jobs | 🏢 {df['company'].nunique():,} companies")
