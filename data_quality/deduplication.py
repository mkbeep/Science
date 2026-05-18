"""
ADVANCED DEDUPLICATION SYSTEM
Xử lý dữ liệu trùng lặp với nhiều chiến lược khác nhau
"""

import hashlib
import sqlite3
from typing import Dict, Any, List, Tuple, Set
from datetime import datetime
import pandas as pd
from difflib import SequenceMatcher


class DeduplicationEngine:
    """Engine xử lý trùng lặp dữ liệu với nhiều phương pháp"""
    
    def __init__(self, db_path: str = '../it_jobs_vietnam.db'):
        self.db_path = db_path
        self.duplicate_stats = {
            'exact_duplicates': 0,
            'fuzzy_duplicates': 0,
            'url_duplicates': 0,
            'content_duplicates': 0,
            'total_removed': 0
        }
    
    # ========================================================================
    # PHƯƠNG PHÁP 1: EXACT DUPLICATE - Trùng hoàn toàn
    # ========================================================================
    
    def generate_exact_fingerprint(self, job: Dict[str, Any]) -> str:
        """
        Tạo fingerprint chính xác từ (title, company, url)
        Dùng để phát hiện trùng lặp hoàn toàn
        """
        title = str(job.get('title', '')).strip().lower()
        company = str(job.get('company', '')).strip().lower()
        url = str(job.get('url', '')).strip().lower()
        
        content = f"{title}|{company}|{url}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def remove_exact_duplicates(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Loại bỏ các job trùng lặp hoàn toàn
        Giữ lại job đầu tiên (hoặc job mới nhất)
        """
        seen_fingerprints = set()
        unique_jobs = []
        
        for job in jobs:
            fingerprint = self.generate_exact_fingerprint(job)
            
            if fingerprint not in seen_fingerprints:
                seen_fingerprints.add(fingerprint)
                unique_jobs.append(job)
            else:
                self.duplicate_stats['exact_duplicates'] += 1
        
        return unique_jobs
    
    # ========================================================================
    # PHƯƠNG PHÁP 2: FUZZY DUPLICATE - Trùng gần giống
    # ========================================================================
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Tính độ tương đồng giữa 2 chuỗi (0.0 - 1.0)
        Sử dụng SequenceMatcher
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def is_fuzzy_duplicate(
        self, 
        job1: Dict[str, Any], 
        job2: Dict[str, Any],
        title_threshold: float = 0.85,
        company_threshold: float = 0.90
    ) -> bool:
        """
        Kiểm tra 2 job có phải fuzzy duplicate không
        
        Tiêu chí:
        - Title tương đồng >= 85%
        - Company tương đồng >= 90%
        - Location giống nhau (nếu có)
        """
        title1 = str(job1.get('title', '')).strip()
        title2 = str(job2.get('title', '')).strip()
        
        company1 = str(job1.get('company', '')).strip()
        company2 = str(job2.get('company', '')).strip()
        
        # Kiểm tra title similarity
        title_sim = self.calculate_similarity(title1, title2)
        if title_sim < title_threshold:
            return False
        
        # Kiểm tra company similarity
        company_sim = self.calculate_similarity(company1, company2)
        if company_sim < company_threshold:
            return False
        
        # Kiểm tra location (nếu có)
        loc1 = str(job1.get('location', '')).strip().lower()
        loc2 = str(job2.get('location', '')).strip().lower()
        
        if loc1 and loc2 and loc1 != loc2:
            return False
        
        return True
    
    def remove_fuzzy_duplicates(
        self, 
        jobs: List[Dict[str, Any]],
        title_threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Loại bỏ các job trùng lặp gần giống
        Sử dụng thuật toán so sánh từng cặp
        
        Note: Phương pháp này chậm với dataset lớn (O(n²))
        Nên chạy sau khi đã loại bỏ exact duplicates
        """
        unique_jobs = []
        
        for job in jobs:
            is_duplicate = False
            
            for existing_job in unique_jobs:
                if self.is_fuzzy_duplicate(job, existing_job, title_threshold):
                    is_duplicate = True
                    self.duplicate_stats['fuzzy_duplicates'] += 1
                    break
            
            if not is_duplicate:
                unique_jobs.append(job)
        
        return unique_jobs
    
    # ========================================================================
    # PHƯƠNG PHÁP 3: URL-BASED DUPLICATE - Trùng theo URL
    # ========================================================================
    
    def normalize_url(self, url: str) -> str:
        """
        Chuẩn hóa URL để so sánh
        Loại bỏ query parameters, trailing slash, etc.
        """
        if not url:
            return ''
        
        url = url.strip().lower()
        
        # Remove query parameters
        if '?' in url:
            url = url.split('?')[0]
        
        # Remove fragment
        if '#' in url:
            url = url.split('#')[0]
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        return url
    
    def remove_url_duplicates(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Loại bỏ các job có cùng URL
        """
        seen_urls = set()
        unique_jobs = []
        
        for job in jobs:
            url = self.normalize_url(job.get('url', ''))
            
            if not url:
                unique_jobs.append(job)
                continue
            
            if url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
            else:
                self.duplicate_stats['url_duplicates'] += 1
        
        return unique_jobs
    
    # ========================================================================
    # PHƯƠNG PHÁP 4: CONTENT-BASED DUPLICATE - Trùng theo nội dung
    # ========================================================================
    
    def generate_content_fingerprint(self, job: Dict[str, Any]) -> str:
        """
        Tạo fingerprint từ nội dung job (description + requirements)
        Dùng để phát hiện job giống nhau về nội dung
        """
        description = str(job.get('description', '')).strip().lower()
        requirements = str(job.get('requirements', '')).strip().lower()
        
        # Chỉ tạo fingerprint nếu có nội dung
        if not description and not requirements:
            return ''
        
        content = f"{description}|{requirements}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def remove_content_duplicates(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Loại bỏ các job có nội dung giống nhau
        """
        seen_contents = set()
        unique_jobs = []
        
        for job in jobs:
            content_fp = self.generate_content_fingerprint(job)
            
            if not content_fp:
                unique_jobs.append(job)
                continue
            
            if content_fp not in seen_contents:
                seen_contents.add(content_fp)
                unique_jobs.append(job)
            else:
                self.duplicate_stats['content_duplicates'] += 1
        
        return unique_jobs
    
    # ========================================================================
    # PHƯƠNG PHÁP 5: DATABASE-BASED DEDUPLICATION
    # ========================================================================
    
    def deduplicate_in_database(self, table_name: str = 'jobs_realtime') -> int:
        """
        Loại bỏ trùng lặp trực tiếp trong database
        Sử dụng SQL để tối ưu hiệu suất
        
        Returns:
            Số lượng bản ghi bị xóa
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tạo bảng tạm để lưu job_id cần giữ lại
        cursor.execute("""
            CREATE TEMP TABLE IF NOT EXISTS jobs_to_keep AS
            SELECT MIN(rowid) as rowid
            FROM {table}
            GROUP BY title, company, url
        """.format(table=table_name))
        
        # Đếm số bản ghi trùng lặp
        cursor.execute("""
            SELECT COUNT(*) FROM {table}
            WHERE rowid NOT IN (SELECT rowid FROM jobs_to_keep)
        """.format(table=table_name))
        
        duplicates_count = cursor.fetchone()[0]
        
        # Xóa các bản ghi trùng lặp
        cursor.execute("""
            DELETE FROM {table}
            WHERE rowid NOT IN (SELECT rowid FROM jobs_to_keep)
        """.format(table=table_name))
        
        conn.commit()
        conn.close()
        
        return duplicates_count
    
    # ========================================================================
    # PHƯƠNG PHÁP TỔNG HỢP
    # ========================================================================
    
    def deduplicate_all(
        self, 
        jobs: List[Dict[str, Any]],
        use_exact: bool = True,
        use_url: bool = True,
        use_fuzzy: bool = False,  # Tắt mặc định vì chậm
        use_content: bool = False,  # Tắt mặc định vì cần description
        fuzzy_threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Áp dụng tất cả các phương pháp deduplication
        
        Args:
            jobs: Danh sách jobs cần xử lý
            use_exact: Loại bỏ trùng lặp hoàn toàn
            use_url: Loại bỏ trùng URL
            use_fuzzy: Loại bỏ trùng gần giống (chậm)
            use_content: Loại bỏ trùng nội dung
            fuzzy_threshold: Ngưỡng similarity cho fuzzy matching
        
        Returns:
            Danh sách jobs đã loại bỏ trùng lặp
        """
        original_count = len(jobs)
        print(f"Starting deduplication: {original_count} jobs")
        
        # 1. Exact duplicates (nhanh nhất)
        if use_exact:
            jobs = self.remove_exact_duplicates(jobs)
            print(f"After exact dedup: {len(jobs)} jobs")
        
        # 2. URL duplicates (nhanh)
        if use_url:
            jobs = self.remove_url_duplicates(jobs)
            print(f"After URL dedup: {len(jobs)} jobs")
        
        # 3. Content duplicates (trung bình)
        if use_content:
            jobs = self.remove_content_duplicates(jobs)
            print(f"After content dedup: {len(jobs)} jobs")
        
        # 4. Fuzzy duplicates (chậm nhất - chỉ dùng khi cần)
        if use_fuzzy:
            print("Running fuzzy deduplication (this may take a while)...")
            jobs = self.remove_fuzzy_duplicates(jobs, fuzzy_threshold)
            print(f"After fuzzy dedup: {len(jobs)} jobs")
        
        self.duplicate_stats['total_removed'] = original_count - len(jobs)
        
        return jobs
    
    def get_stats(self) -> Dict[str, int]:
        """Lấy thống kê về các loại trùng lặp đã xử lý"""
        return self.duplicate_stats
    
    def print_stats(self):
        """In thống kê chi tiết"""
        print("\n" + "="*60)
        print("DEDUPLICATION STATISTICS")
        print("="*60)
        print(f"Exact duplicates removed:   {self.duplicate_stats['exact_duplicates']:,}")
        print(f"URL duplicates removed:     {self.duplicate_stats['url_duplicates']:,}")
        print(f"Content duplicates removed: {self.duplicate_stats['content_duplicates']:,}")
        print(f"Fuzzy duplicates removed:   {self.duplicate_stats['fuzzy_duplicates']:,}")
        print("-"*60)
        print(f"TOTAL REMOVED:              {self.duplicate_stats['total_removed']:,}")
        print("="*60)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == '__main__':
    # Example 1: Deduplicate a list of jobs
    engine = DeduplicationEngine()
    
    sample_jobs = [
        {
            'job_id': '1',
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'url': 'https://example.com/job/1',
            'location': 'Hà Nội'
        },
        {
            'job_id': '2',
            'title': 'Senior Python Developer',  # Exact duplicate
            'company': 'Tech Corp',
            'url': 'https://example.com/job/1',
            'location': 'Hà Nội'
        },
        {
            'job_id': '3',
            'title': 'Senior Python Dev',  # Fuzzy duplicate
            'company': 'Tech Corp',
            'url': 'https://example.com/job/3',
            'location': 'Hà Nội'
        },
    ]
    
    # Deduplicate
    unique_jobs = engine.deduplicate_all(
        sample_jobs,
        use_exact=True,
        use_url=True,
        use_fuzzy=True,
        fuzzy_threshold=0.85
    )
    
    print(f"\nOriginal: {len(sample_jobs)} jobs")
    print(f"After deduplication: {len(unique_jobs)} jobs")
    
    engine.print_stats()
    
    # Example 2: Deduplicate in database
    print("\n" + "="*60)
    print("DATABASE DEDUPLICATION")
    print("="*60)
    
    try:
        removed = engine.deduplicate_in_database('jobs_realtime')
        print(f"Removed {removed:,} duplicate records from database")
    except Exception as e:
        print(f"Error: {e}")
