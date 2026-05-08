"""
Top Locations Analysis Module
"""

from .analyze_locations import (
    load_data,
    normalize_location,
    get_top_locations,
    plot_top_locations,
    get_location_salary,
    plot_location_salary,
    generate_report
)

__all__ = [
    'load_data',
    'normalize_location',
    'get_top_locations',
    'plot_top_locations',
    'get_location_salary',
    'plot_location_salary',
    'generate_report'
]
