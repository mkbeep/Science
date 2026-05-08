"""
PHASE 5: SEARCH & QUERY FEATURE
SQL-based search functionality for IT job database
"""

import sqlite3
import pandas as pd

class JobSearchEngine:
    """Search engine for IT jobs database"""
    
    def __init__(self, db_file='it_jobs_vietnam.db'):
        self.db_file = db_file
    
    def _execute_query(self, query, params=()):
        """Execute SQL query and return results"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_by_skill(self, skill_name, limit=10):
        """Search jobs by skill using LIKE"""
        query = """
        SELECT DISTINCT j.job_id, j.title, j.company, j.location, j.job_level
        FROM jobs j
        JOIN job_skills js ON j.job_id = js.job_id
        WHERE js.skill_name LIKE ?
        ORDER BY j.job_id DESC
        LIMIT ?
        """
        results = self._execute_query(query, (f'%{skill_name}%', limit))
        return results
    
    def search_by_location(self, city, limit=10):
        """Search jobs by city using WHERE"""
        query = """
        SELECT job_id, title, company, location, job_level, salary_min, salary_max
        FROM jobs
        WHERE location LIKE ?
        ORDER BY job_id DESC
        LIMIT ?
        """
        results = self._execute_query(query, (f'%{city}%', limit))
        return results
    
    def get_top_companies(self, limit=10):
        """Get top companies by job count using GROUP BY"""
        query = """
        SELECT company, COUNT(*) as job_count
        FROM jobs
        GROUP BY company
        ORDER BY job_count DESC
        LIMIT ?
        """
        results = self._execute_query(query, (limit,))
        return results
    
    def get_top_skills(self, limit=15):
        """Get top skills by demand using COUNT and GROUP BY"""
        query = """
        SELECT skill_name, COUNT(*) as demand_count
        FROM job_skills
        GROUP BY skill_name
        ORDER BY demand_count DESC
        LIMIT ?
        """
        results = self._execute_query(query, (limit,))
        return results
    
    def get_high_salary_jobs(self, min_salary=20000000, limit=10):
        """Get high salary jobs using ORDER BY"""
        query = """
        SELECT job_id, title, company, location, 
               salary_min, salary_max, 
               (salary_min + salary_max) / 2 as avg_salary
        FROM jobs
        WHERE salary_min > 0 AND salary_max > 0
        AND (salary_min + salary_max) / 2 >= ?
        ORDER BY avg_salary DESC
        LIMIT ?
        """
        results = self._execute_query(query, (min_salary, limit))
        return results
    
    def search_by_company_and_skill(self, company, skill):
        """Advanced search: company AND skill"""
        query = """
        SELECT DISTINCT j.job_id, j.title, j.company, j.location
        FROM jobs j
        JOIN job_skills js ON j.job_id = js.job_id
        WHERE j.company LIKE ?
        AND js.skill_name LIKE ?
        ORDER BY j.job_id DESC
        """
        results = self._execute_query(query, (f'%{company}%', f'%{skill}%'))
        return results
    
    def get_jobs_by_level(self, job_level, limit=10):
        """Search jobs by experience level"""
        query = """
        SELECT job_id, title, company, location, job_level
        FROM jobs
        WHERE job_level = ?
        ORDER BY job_id DESC
        LIMIT ?
        """
        results = self._execute_query(query, (job_level, limit))
        return results
    
    def get_location_statistics(self):
        """Get job distribution by location"""
        query = """
        SELECT location, COUNT(*) as job_count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage
        FROM jobs
        GROUP BY location
        ORDER BY job_count DESC
        LIMIT 10
        """
        results = self._execute_query(query)
        return results

def print_results(title, results, headers):
    """Pretty print query results"""
    print(f"\n{'='*100}")
    print(f"{title}")
    print(f"{'='*100}")
    
    if not results:
        print("No results found.")
        return
    
    # Calculate column widths based on actual data
    num_cols = len(results[0]) if results else len(headers)
    col_widths = [max(len(str(headers[i])) if i < len(headers) else 10, 10) for i in range(num_cols)]
    
    for row in results:
        for i, item in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(item)))
    
    # Limit max width
    col_widths = [min(w, 40) for w in col_widths]
    
    # Print header
    header_parts = []
    for i in range(num_cols):
        h = headers[i] if i < len(headers) else f"Col{i+1}"
        header_parts.append(f"{h:<{col_widths[i]}}")
    print(" | ".join(header_parts))
    print("-" * 100)
    
    # Print rows
    for row in results:
        row_parts = []
        for i, item in enumerate(row):
            if i < len(col_widths):
                row_parts.append(f"{str(item)[:col_widths[i]]:<{col_widths[i]}}")
        print(" | ".join(row_parts))
    
    print(f"\nTotal results: {len(results)}")

def demo_search_features():
    """Demonstrate all search features"""
    print("\n" + "="*100)
    print("PHASE 5: SEARCH & QUERY FEATURE DEMONSTRATION")
    print("="*100)
    
    search = JobSearchEngine()
    
    # 1. Search by skill (LIKE)
    print("\n[1] SEARCH BY SKILL (SQL: LIKE)")
    print("Query: Find jobs requiring 'Python'")
    results = search.search_by_skill('Python', limit=5)
    print_results("Jobs requiring Python", results, 
                 ['Job ID', 'Title', 'Company', 'Location', 'Level'])
    
    # 2. Search by location (WHERE)
    print("\n[2] SEARCH BY LOCATION (SQL: WHERE)")
    print("Query: Find jobs in 'Hà Nội'")
    results = search.search_by_location('Hà Nội', limit=5)
    print_results("Jobs in Hà Nội", results,
                 ['Job ID', 'Title', 'Company', 'Location', 'Level'])
    
    # 3. Top companies (GROUP BY)
    print("\n[3] TOP COMPANIES (SQL: GROUP BY, COUNT)")
    print("Query: Companies with most job postings")
    results = search.get_top_companies(limit=10)
    print_results("Top 10 Companies", results,
                 ['Company', 'Job Count'])
    
    # 4. Top skills (COUNT)
    print("\n[4] TOP SKILLS (SQL: COUNT, GROUP BY)")
    print("Query: Most demanded skills")
    results = search.get_top_skills(limit=10)
    print_results("Top 10 Skills", results,
                 ['Skill', 'Demand Count'])
    
    # 5. High salary jobs (ORDER BY)
    print("\n[5] HIGH SALARY JOBS (SQL: ORDER BY)")
    print("Query: Jobs with salary >= 20M VND")
    results = search.get_high_salary_jobs(min_salary=20000000, limit=5)
    if results:
        print_results("High Salary Jobs", results,
                     ['Job ID', 'Title', 'Company', 'Location', 'Avg Salary'])
    else:
        print("\nNo high salary data available (most jobs don't list salary)")
    
    # 6. Advanced search
    print("\n[6] ADVANCED SEARCH (SQL: JOIN, AND)")
    print("Query: Jobs at 'FPT' requiring 'Java'")
    results = search.search_by_company_and_skill('FPT', 'Java')
    if results:
        print_results("FPT Jobs requiring Java", results,
                     ['Job ID', 'Title', 'Company', 'Location'])
    else:
        print("\nNo results found for this combination")
    
    # 7. Search by level
    print("\n[7] SEARCH BY JOB LEVEL (SQL: WHERE)")
    print("Query: Entry level positions")
    results = search.get_jobs_by_level('Fresher/Entry level', limit=5)
    print_results("Fresher/Entry Level Jobs", results,
                 ['Job ID', 'Title', 'Company', 'Location', 'Level'])
    
    # 8. Location statistics
    print("\n[8] LOCATION STATISTICS (SQL: GROUP BY, Subquery)")
    print("Query: Job distribution by location")
    results = search.get_location_statistics()
    print_results("Top 10 Locations", results,
                 ['Location', 'Job Count', 'Percentage'])
    
    # Summary
    print("\n" + "="*100)
    print("SEARCH FEATURES SUMMARY")
    print("="*100)
    print("✓ Search by skill (LIKE)")
    print("✓ Search by location (WHERE)")
    print("✓ Top companies (GROUP BY, COUNT)")
    print("✓ Top skills (COUNT, GROUP BY)")
    print("✓ High salary jobs (ORDER BY)")
    print("✓ Advanced search (JOIN, AND)")
    print("✓ Search by job level (WHERE)")
    print("✓ Location statistics (GROUP BY, Subquery)")
    print("\nSQL Features Used:")
    print("  • SELECT, FROM, WHERE")
    print("  • JOIN (INNER JOIN)")
    print("  • GROUP BY, COUNT()")
    print("  • ORDER BY, LIMIT")
    print("  • LIKE (pattern matching)")
    print("  • Subqueries")
    print("  • Aggregate functions")
    print("="*100 + "\n")

def interactive_search():
    """Interactive search menu"""
    search = JobSearchEngine()
    
    while True:
        print("\n" + "="*60)
        print("IT JOBS SEARCH SYSTEM")
        print("="*60)
        print("1. Search by skill")
        print("2. Search by location")
        print("3. View top companies")
        print("4. View top skills")
        print("5. View high salary jobs")
        print("6. Search by job level")
        print("7. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            skill = input("Enter skill name: ").strip()
            results = search.search_by_skill(skill, limit=10)
            print_results(f"Jobs requiring '{skill}'", results,
                         ['Job ID', 'Title', 'Company', 'Location', 'Level'])
        
        elif choice == '2':
            city = input("Enter city name: ").strip()
            results = search.search_by_location(city, limit=10)
            print_results(f"Jobs in '{city}'", results,
                         ['Job ID', 'Title', 'Company', 'Location', 'Level'])
        
        elif choice == '3':
            results = search.get_top_companies(limit=15)
            print_results("Top 15 Companies", results,
                         ['Company', 'Job Count'])
        
        elif choice == '4':
            results = search.get_top_skills(limit=20)
            print_results("Top 20 Skills", results,
                         ['Skill', 'Demand Count'])
        
        elif choice == '5':
            results = search.get_high_salary_jobs(min_salary=15000000, limit=10)
            if results:
                print_results("High Salary Jobs (>15M VND)", results,
                             ['Job ID', 'Title', 'Company', 'Location', 'Avg Salary'])
            else:
                print("\nNo salary data available")
        
        elif choice == '6':
            print("\nJob Levels:")
            print("  1. Fresher/Entry level")
            print("  2. Experienced (non-manager)")
            print("  3. Manager")
            print("  4. Director and above")
            level_choice = input("Choose level (1-4): ").strip()
            
            levels = {
                '1': 'Fresher/Entry level',
                '2': 'Experienced (non-manager)',
                '3': 'Manager',
                '4': 'Director and above'
            }
            
            if level_choice in levels:
                results = search.get_jobs_by_level(levels[level_choice], limit=10)
                print_results(f"{levels[level_choice]} Jobs", results,
                             ['Job ID', 'Title', 'Company', 'Location', 'Level'])
        
        elif choice == '7':
            print("\nThank you for using IT Jobs Search System!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    # Run demonstration
    demo_search_features()
    
    # Optional: Interactive mode
    print("\nWould you like to try interactive search? (y/n): ", end='')
    if input().strip().lower() == 'y':
        interactive_search()
