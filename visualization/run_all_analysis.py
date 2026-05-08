"""
Run All Visualization Analysis
"""

import subprocess
import sys

SCRIPTS = [
    ('visualization/city_analysis.py', 'City Analysis'),
    ('visualization/ai_trend_analysis.py', 'AI/ML Trends'),
    ('visualization/salary_analysis.py', 'Salary Analysis'),
    ('visualization/dashboard.py', 'Dashboard & Report'),
]

def run_script(script, desc):
    """Run a Python script"""
    print(f"\n{'='*60}\n{desc}\n{'='*60}")
    try:
        subprocess.run([sys.executable, script], check=True)
        print(f"✓ {desc} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all analysis"""
    print("\n" + "="*60)
    print("RUNNING ALL VISUALIZATIONS")
    print("="*60)
    
    results = [(desc, run_script(script, desc)) for script, desc in SCRIPTS]
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for desc, success in results:
        print(f"{'✓' if success else '✗'} {desc}")
    
    print(f"\n{sum(s for _, s in results)}/{len(results)} completed")
    print("\nGenerated files in visualization/:")
    print("  • city_analysis.png")
    print("  • ai_trend_analysis.png")
    print("  • salary_analysis.png")
    print("  • technology_trends.png")
    print("  • comprehensive_dashboard.png")
    print("  • final_report.txt")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
