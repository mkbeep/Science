"""
SALARY PARSER - Xử lý thông tin lương
Parse và chuẩn hóa thông tin lương từ VietnamWorks
"""

import re
from typing import Dict, Optional, Tuple


def parse_salary_text(salary_text: str) -> Dict[str, Optional[float]]:
    """
    Parse salary text từ VietnamWorks
    
    Ví dụ:
    - "15 - 25 triệu VND" -> min: 15, max: 25, unit: 'month'
    - "180 - 300 triệu VND/năm" -> min: 15, max: 25, unit: 'month' (chia 12)
    - "Thỏa thuận" -> min: None, max: None
    - "Up to 2000 USD" -> min: None, max: 2000, currency: 'USD'
    - "Tới 30tr ₫/tháng" -> min: None, max: 30, unit: 'month'
    - "50tr-70tr ₫/tháng" -> min: 50, max: 70, unit: 'month'
    
    Returns:
        {
            'min': float or None,
            'max': float or None,
            'currency': 'VND' or 'USD',
            'unit': 'month' or 'year',
            'original': original text
        }
    """
    if not salary_text or not isinstance(salary_text, str):
        return {
            'min': None,
            'max': None,
            'currency': 'VND',
            'unit': 'month',
            'original': ''
        }
    
    salary_text = salary_text.strip()
    original = salary_text
    
    # Chuẩn hóa text
    text_lower = salary_text.lower()
    
    # Kiểm tra "Thỏa thuận" hoặc "Negotiable"
    if any(keyword in text_lower for keyword in ['thỏa thuận', 'thoả thuận', 'thương lượng', 'negotiable', 'competitive']):
        return {
            'min': None,
            'max': None,
            'currency': 'VND',
            'unit': 'month',
            'original': original
        }
    
    # Xác định currency
    currency = 'VND'
    if 'usd' in text_lower or '$' in text_lower:
        currency = 'USD'
    
    # Xác định unit (month/year)
    unit = 'month'
    if any(keyword in text_lower for keyword in ['/năm', 'năm', '/year', 'yearly', 'per year', 'annually']):
        unit = 'year'
    
    # Extract numbers - cẩn thận với format "30tr" (30 triệu)
    # Pattern: tìm số (có thể có dấu phẩy hoặc chấm), có thể theo sau bởi "tr" (triệu)
    # Ví dụ: "30tr", "30,000", "30.5", "2,000"
    numbers = re.findall(r'(\d+(?:[.,]\d+)?)\s*(?:tr|triệu)?', salary_text, re.IGNORECASE)
    
    if not numbers:
        return {
            'min': None,
            'max': None,
            'currency': currency,
            'unit': unit,
            'original': original
        }
    
    # Convert to float
    parsed_numbers = []
    for num in numbers:
        try:
            # Replace comma with dot for decimal
            num_clean = num.replace(',', '.')
            value = float(num_clean)
            
            # Nếu số quá lớn (> 1000) và có "tr" hoặc "triệu" trong text gần đó
            # thì đó là format "30000tr" (30 nghìn triệu) -> chia cho 1000
            # Nhưng thường thì "30tr" = 30 triệu, không cần chia
            # Chỉ chia nếu số > 1000 và không có "tr" trong text
            if value > 1000 and ('tr' not in text_lower and 'triệu' not in text_lower):
                # Có thể là format "30000" (30 nghìn) -> chia 1000 để thành 30 triệu
                value = value / 1000
            
            parsed_numbers.append(value)
        except ValueError:
            continue
    
    if not parsed_numbers:
        return {
            'min': None,
            'max': None,
            'currency': currency,
            'unit': unit,
            'original': original
        }
    
    # Determine min and max
    if len(parsed_numbers) == 1:
        # Chỉ có 1 số
        if 'up to' in text_lower or 'tới' in text_lower or 'đến' in text_lower:
            min_salary = None
            max_salary = parsed_numbers[0]
        elif 'from' in text_lower or 'từ' in text_lower:
            min_salary = parsed_numbers[0]
            max_salary = None
        else:
            # Mặc định là max
            min_salary = None
            max_salary = parsed_numbers[0]
    else:
        # Có nhiều số, lấy min và max
        min_salary = min(parsed_numbers)
        max_salary = max(parsed_numbers)
    
    return {
        'min': min_salary,
        'max': max_salary,
        'currency': currency,
        'unit': unit,
        'original': original
    }


def normalize_salary(
    salary_min: Optional[float],
    salary_max: Optional[float],
    salary_text: str = '',
    api_min: Optional[float] = None,
    api_max: Optional[float] = None
) -> Dict[str, Optional[float]]:
    """
    Chuẩn hóa thông tin lương thành lương tháng (VND triệu)
    
    Priority:
    1. API values (salaryMin, salaryMax) - đã chuẩn hóa
    2. Parse từ salary text
    
    Args:
        salary_min: Min salary từ API hoặc parse
        salary_max: Max salary từ API hoặc parse
        salary_text: Text mô tả lương
        api_min: salaryMin từ API VietnamWorks
        api_max: salaryMax từ API VietnamWorks
    
    Returns:
        {
            'salary_min_monthly': float (triệu VND/tháng),
            'salary_max_monthly': float (triệu VND/tháng),
            'salary_currency': 'VND' or 'USD',
            'salary_text': original text,
            'is_negotiable': bool
        }
    """
    result = {
        'salary_min_monthly': None,
        'salary_max_monthly': None,
        'salary_currency': 'VND',
        'salary_text': salary_text or '',
        'is_negotiable': False
    }
    
    # Check if negotiable
    if salary_text:
        text_lower = salary_text.lower()
        if any(keyword in text_lower for keyword in ['thỏa thuận', 'thoả thuận', 'negotiable', 'competitive']):
            result['is_negotiable'] = True
            return result
    
    # Priority 1: Use API values if available
    if api_min is not None or api_max is not None:
        # API values từ VietnamWorks thường là triệu VND/tháng
        result['salary_min_monthly'] = api_min
        result['salary_max_monthly'] = api_max
        result['salary_currency'] = 'VND'
        return result
    
    # Priority 2: Parse from salary_text
    if salary_text:
        parsed = parse_salary_text(salary_text)
        
        min_val = parsed['min']
        max_val = parsed['max']
        currency = parsed['currency']
        unit = parsed['unit']
        
        # Convert to monthly if yearly
        if unit == 'year':
            if min_val is not None:
                min_val = min_val / 12
            if max_val is not None:
                max_val = max_val / 12
        
        result['salary_min_monthly'] = min_val
        result['salary_max_monthly'] = max_val
        result['salary_currency'] = currency
        
        return result
    
    # Priority 3: Use provided min/max (fallback)
    result['salary_min_monthly'] = salary_min
    result['salary_max_monthly'] = salary_max
    
    return result


def format_salary_display(
    salary_min: Optional[float],
    salary_max: Optional[float],
    currency: str = 'VND',
    is_negotiable: bool = False
) -> str:
    """
    Format salary cho hiển thị
    
    Returns:
        String như "15 - 25 triệu VND" hoặc "Thỏa thuận"
    """
    if is_negotiable:
        return "Thỏa thuận"
    
    if salary_min is None and salary_max is None:
        return "Không xác định"
    
    currency_symbol = 'triệu VND' if currency == 'VND' else 'USD'
    
    if salary_min is not None and salary_max is not None:
        return f"{salary_min:.1f} - {salary_max:.1f} {currency_symbol}"
    elif salary_max is not None:
        return f"Lên đến {salary_max:.1f} {currency_symbol}"
    elif salary_min is not None:
        return f"Từ {salary_min:.1f} {currency_symbol}"
    
    return "Không xác định"


def calculate_salary_stats(jobs: list) -> Dict:
    """
    Tính thống kê lương từ danh sách jobs
    
    Returns:
        {
            'avg_min': float,
            'avg_max': float,
            'median_min': float,
            'median_max': float,
            'jobs_with_salary': int,
            'jobs_negotiable': int
        }
    """
    min_salaries = []
    max_salaries = []
    negotiable_count = 0
    
    for job in jobs:
        if job.get('is_negotiable'):
            negotiable_count += 1
            continue
        
        if job.get('salary_min_monthly') is not None:
            min_salaries.append(job['salary_min_monthly'])
        
        if job.get('salary_max_monthly') is not None:
            max_salaries.append(job['salary_max_monthly'])
    
    stats = {
        'jobs_with_salary': len(min_salaries) + len(max_salaries),
        'jobs_negotiable': negotiable_count,
        'avg_min': None,
        'avg_max': None,
        'median_min': None,
        'median_max': None
    }
    
    if min_salaries:
        stats['avg_min'] = sum(min_salaries) / len(min_salaries)
        sorted_min = sorted(min_salaries)
        mid = len(sorted_min) // 2
        stats['median_min'] = sorted_min[mid]
    
    if max_salaries:
        stats['avg_max'] = sum(max_salaries) / len(max_salaries)
        sorted_max = sorted(max_salaries)
        mid = len(sorted_max) // 2
        stats['median_max'] = sorted_max[mid]
    
    return stats


# ============================================================================
# TESTS
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("SALARY PARSER TESTS")
    print("="*70)
    
    test_cases = [
        "15 - 25 triệu VND",
        "180 - 300 triệu VND/năm",
        "Thỏa thuận",
        "Up to 2000 USD",
        "From 20 triệu",
        "1000 - 1500 USD/month",
        "Lương tháng 13, 14",
        "Competitive salary",
        "25 triệu VND/tháng",
        "300 triệu/năm",
    ]
    
    print("\n[TEST 1] Parse salary text:")
    print("-"*70)
    for text in test_cases:
        result = parse_salary_text(text)
        print(f"\nInput:  {text}")
        print(f"Output: min={result['min']}, max={result['max']}, "
              f"currency={result['currency']}, unit={result['unit']}")
    
    print("\n\n[TEST 2] Normalize salary:")
    print("-"*70)
    
    # Test case 1: Lương năm -> chuyển thành tháng
    result1 = normalize_salary(
        salary_min=None,
        salary_max=None,
        salary_text="180 - 300 triệu VND/năm"
    )
    print(f"\nCase 1: Lương năm")
    print(f"Input:  180 - 300 triệu VND/năm")
    print(f"Output: {result1['salary_min_monthly']:.1f} - {result1['salary_max_monthly']:.1f} triệu VND/tháng")
    
    # Test case 2: API values
    result2 = normalize_salary(
        salary_min=None,
        salary_max=None,
        salary_text="",
        api_min=15.0,
        api_max=25.0
    )
    print(f"\nCase 2: API values")
    print(f"Input:  api_min=15, api_max=25")
    print(f"Output: {result2['salary_min_monthly']} - {result2['salary_max_monthly']} triệu VND/tháng")
    
    # Test case 3: Thỏa thuận
    result3 = normalize_salary(
        salary_min=None,
        salary_max=None,
        salary_text="Thỏa thuận"
    )
    print(f"\nCase 3: Thỏa thuận")
    print(f"Input:  Thỏa thuận")
    print(f"Output: is_negotiable={result3['is_negotiable']}")
    
    print("\n\n[TEST 3] Format display:")
    print("-"*70)
    
    display1 = format_salary_display(15.0, 25.0, 'VND', False)
    print(f"15-25 triệu VND: {display1}")
    
    display2 = format_salary_display(None, None, 'VND', True)
    print(f"Negotiable: {display2}")
    
    display3 = format_salary_display(None, 2000, 'USD', False)
    print(f"Up to 2000 USD: {display3}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)
