"""
Utility functions for visualization
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set default style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

def load_data(csv_file='clean_it_jobs.csv', db_file='it_jobs_vietnam.db'):
    """Load data from CSV and database"""
    df = pd.read_csv(csv_file)
    conn = sqlite3.connect(db_file)
    return df, conn

def save_plot(filename, dpi=300):
    """Save plot to visualization folder"""
    os.makedirs('visualization', exist_ok=True)
    filepath = os.path.join('visualization', filename)
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    print(f"✓ Saved: {filepath}")
    plt.show()

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(title)
    print('='*60)
