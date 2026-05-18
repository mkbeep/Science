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
    
    # Kiểm tra "Thỏa thuận" / "Thương lượng" hoặc "Negotiable"
    if any(keyword in text_lower for keyword in [
        'thỏa thuận', 'thoả thuận', 'thương lượng', 'thuong luong',
        'negotiable', 'competitive', 'salary negotiable'
    ]):
        return {
            'min': None,
            'max': None,
            'currency': 'VND',
            'unit': 'month',
            'original': original
        }
    
    # Skip non-salary text like "Lương tháng 13, 14" (bonus months, not salary amounts)
    if re.match(r'^lương\s+tháng\s+\d', text_lower):
        return {
            'min': None,
            'max': None,
            'currency': 'VND',
            'unit': 'month',
            'original': original
        }
    
    # Xác định currency
    # Lưu ý: VietnamWorks đôi khi hiển thị "$ 50tr-70tr" = VND (không phải USD)
    # Nếu có 'tr' hoặc 'triệu' -> luôn là VND, dù có '$'
    currency = 'VND'
    has_trieu_marker = bool(re.search(r'tr(?:iệu)?', text_lower))
    if ('usd' in text_lower or '$' in text_lower) and not has_trieu_marker:
        currency = 'USD'

    
    # Xác định unit (month/year)
    unit = 'month'
    if any(keyword in text_lower for keyword in ['/năm', 'năm', '/year', 'yearly', 'per year', 'annually']):
        unit = 'year'
    
    # ===================================================================
    # Extract numbers - xử lý cẩn thận các format:
    #   "30tr", "30,000,000", "30.000.000", "30.5", "2,000", "15 - 25"
    #
    # Regex giải thích:
    #   (\d{1,3}(?:[.,]\d{3})*  -> số có dấu phân cách hàng nghìn: 30,000,000
    #   |                       -> hoặc
    #   \d+(?:[.,]\d+)?         -> số thường hoặc số thập phân: 30, 30.5
    #   )
    #   \s*(tr(?:iệu)?)?        -> có thể theo sau bởi "tr" hoặc "triệu"
    # ===================================================================
    raw_matches = re.findall(
        r'(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)\s*(tr(?:iệu)?)?',
        salary_text,
        re.IGNORECASE,
    )
    
    if not raw_matches:
        return {
            'min': None,
            'max': None,
            'currency': currency,
            'unit': unit,
            'original': original
        }
    
    # Kiểm tra toàn cục: text có chứa "tr" hoặc "triệu" không?
    has_trieu_in_text = bool(re.search(r'tr(?:iệu)?', text_lower))
    
    # Convert to float
    parsed_numbers = []
    for num_str, trieu_suffix in raw_matches:
        try:
            # Xác định dấu phân cách: dấu phẩy hay dấu chấm là hàng nghìn?
            # Nếu có pattern như "30,000,000" hoặc "30.000.000" -> hàng nghìn
            # Nếu chỉ có 1 dấu và phần sau có 1-2 chữ số -> thập phân (vd: "30.5")
            
            comma_count = num_str.count(',')
            dot_count = num_str.count('.')
            
            if comma_count + dot_count == 0:
                # Không có dấu phân cách -> số nguyên
                value = float(num_str)
            elif comma_count > 0 and dot_count == 0:
                # Chỉ có dấu phẩy
                # Kiểm tra xem có phải dấu phân cách hàng nghìn không
                parts = num_str.split(',')
                if all(len(p) == 3 for p in parts[1:]):
                    # "30,000,000" hoặc "1,000" -> hàng nghìn
                    value = float(num_str.replace(',', ''))
                else:
                    # "30,5" -> thập phân (European format)
                    value = float(num_str.replace(',', '.'))
            elif dot_count > 0 and comma_count == 0:
                # Chỉ có dấu chấm
                parts = num_str.split('.')
                if all(len(p) == 3 for p in parts[1:]) and dot_count > 1:
                    # "30.000.000" -> hàng nghìn (Vietnamese format)
                    value = float(num_str.replace('.', ''))
                elif all(len(p) == 3 for p in parts[1:]) and dot_count == 1:
                    # Ambiguous: "1.000" could be 1000 or 1.0
                    # Trong context lương VN, "1.000" thường = 1000
                    # Nhưng "30.5" = 30.5 (thập phân)
                    if len(parts[-1]) == 3 and len(parts[0]) >= 1:
                        value = float(num_str.replace('.', ''))
                    else:
                        value = float(num_str)
                else:
                    # "30.5" -> thập phân
                    value = float(num_str)
            else:
                # Có cả dấu chấm và dấu phẩy -> xử lý theo format cuối cùng
                # "1,000.50" -> comma = nghìn, dot = thập phân
                # "1.000,50" -> dot = nghìn, comma = thập phân
                last_comma = num_str.rfind(',')
                last_dot = num_str.rfind('.')
                if last_comma > last_dot:
                    # comma cuối -> comma là thập phân, dot là nghìn
                    value = float(num_str.replace('.', '').replace(',', '.'))
                else:
                    # dot cuối -> dot là thập phân, comma là nghìn
                    value = float(num_str.replace(',', ''))
            
            # ---------------------------------------------------------------
            # Chuyển đổi sang đơn vị triệu VND (cho VND) hoặc giữ nguyên (USD)
            # ---------------------------------------------------------------
            is_trieu = bool(trieu_suffix)  # Số này có "tr"/"triệu" đi kèm không
            
            if currency == 'VND':
                if is_trieu:
                    # "30tr" = 30 triệu -> giữ nguyên = 30
                    pass
                elif has_trieu_in_text:
                    # Có "triệu" trong text nhưng không gắn liền số này
                    # vd: "15 - 25 triệu VND" -> 15 và 25 đều là triệu
                    pass
                else:
                    # Không có "tr"/"triệu" trong text
                    # Phải đoán: nếu số lớn -> có thể là VND thô
                    if value >= 1_000_000:
                        # "30000000" = 30 triệu
                        value = value / 1_000_000
                    elif value >= 1_000:
                        # "30000" = 30 nghìn? Khó xác định, nhưng trong context
                        # lương IT VN thường > 1 triệu, nên:
                        # - "30000" -> có thể là 30 triệu (nhập sai format)
                        # Giữ nguyên và để downstream xử lý
                        value = value / 1_000
            # USD: giữ nguyên (không chia), vd: 2000 USD = 2000
            
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
        if any(keyword in text_lower for keyword in [
            'thỏa thuận', 'thoả thuận', 'thương lượng', 'thuong luong',
            'negotiable', 'competitive', 'salary negotiable'
        ]):
            result['is_negotiable'] = True
            return result
    
    # Priority 1: Parse từ salary_text (prettySalary) - chính xác nhất vì có đơn vị rõ ràng
    if salary_text:
        parsed = parse_salary_text(salary_text)
        min_val = parsed['min']
        max_val = parsed['max']
        currency = parsed['currency']
        unit = parsed['unit']
        
        # Nếu parse được giá trị -> dùng ngay
        if min_val is not None or max_val is not None:
            # Bỏ qua JPY / Yên Nhật (¥)
            if '¥' in salary_text or 'jpy' in salary_text.lower():
                pass  # fall through to api values
            else:
                # Convert to monthly if yearly
                if unit == 'year':
                    if min_val is not None:
                        min_val = min_val / 12
                    if max_val is not None:
                        max_val = max_val / 12

                # Sanity check: lọc outliers do parse sai đơn vị
                # VND thực tế: 0.3tr - 200tr/tháng | USD: $50 - $30,000/tháng
                def _in_range(v, curr):
                    if v is None:
                        return True
                    return (0.3 <= v <= 200) if curr == 'VND' else (50 <= v <= 30_000)

                if _in_range(min_val, currency) and _in_range(max_val, currency):
                    result['salary_min_monthly'] = min_val
                    result['salary_max_monthly'] = max_val
                    result['salary_currency'] = currency
                    return result
                # else: giá trị bất hợp lý -> fall through to api values


    
    # Priority 2: Fallback - dùng API values (api_min/api_max) khi text không parse được
    # VietnamWorks API: salaryMin/salaryMax là VND thô (e.g. 15000000) hoặc USD (e.g. 1000)
    if api_min is not None or api_max is not None:
        def _to_million_vnd(val):
            """Chuyển VND thô -> triệu VND."""
            if val is None:
                return None
            if val >= 1_000_000:
                return round(val / 1_000_000, 2)  # 15000000 -> 15.0
            elif val >= 1_000:
                return round(val / 1_000, 2)       # 15000 -> 15.0
            else:
                return val                          # 15 -> 15 (đã là triệu)
        
        # Detect USD: có '$' hoặc 'usd' trong text VÀ không có 'tr'/'triệu' (vì '$50tr' là VND)
        text_lower = (salary_text or '').lower()
        has_dollar_or_usd = ('usd' in text_lower or '$' in text_lower)
        has_trieu = bool(re.search(r'tr(?:iệu)?', text_lower))
        is_usd_job = has_dollar_or_usd and not has_trieu
        
        if is_usd_job:
            result['salary_min_monthly'] = api_min
            result['salary_max_monthly'] = api_max
            result['salary_currency'] = 'USD'
        else:
            result['salary_min_monthly'] = _to_million_vnd(api_min)
            result['salary_max_monthly'] = _to_million_vnd(api_max)
            result['salary_currency'] = 'VND'
        return result
    
    # Priority 3: Use provided min/max (fallback cuối)
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
        # New test cases for bug fixes
        "Tới 30tr ₫/tháng",
        "50tr-70tr ₫/tháng",
        "30,000,000 - 50,000,000 VND",
        "30.000.000 - 50.000.000 VND",
        "30000000",
        "1,000 - 2,000 USD",
        "$2,500 - $3,500",
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
