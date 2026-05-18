"""
DATA VALIDATION & CLEANING SYSTEM
Xử lý dữ liệu xấu với nhiều chiến lược khác nhau
"""

import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import pandas as pd
from enum import Enum


class DataQuality(Enum):
    """Mức độ chất lượng dữ liệu"""
    EXCELLENT = 5  # Đầy đủ tất cả thông tin quan trọng
    GOOD = 4       # Thiếu 1-2 trường không quan trọng
    ACCEPTABLE = 3 # Thiếu một số trường
    POOR = 2       # Thiếu nhiều trường quan trọng
    BAD = 1        # Dữ liệu không sử dụng được


class DataValidator:
    """Engine kiểm tra và làm sạch dữ liệu xấu"""
    
    def __init__(self, db_path: str = '../it_jobs_vietnam.db'):
        self.db_path = db_path
        self.validation_stats = {
            'total_jobs': 0,
            'valid_jobs': 0,
            'invalid_jobs': 0,
            'fixed_jobs': 0,
            'rejected_jobs': 0,
            'quality_scores': []
        }
    
    # ========================================================================
    # VALIDATION RULES - Quy tắc kiểm tra
    # ========================================================================
    
    def validate_required_fields(self, job: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Kiểm tra các trường bắt buộc
        
        Returns:
            (is_valid, missing_fields)
        """
        required_fields = ['title', 'company']
        missing_fields = []
        
        for field in required_fields:
            value = job.get(field, '')
            if not value or str(value).strip() == '':
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
    
    def validate_title(self, title: str) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra và làm sạch job title
        
        Returns:
            (is_valid, cleaned_title)
        """
        if not title or not isinstance(title, str):
            return False, None
        
        title = title.strip()
        
        # Kiểm tra độ dài
        if len(title) < 3:
            return False, None
        
        if len(title) > 200:
            title = title[:200]
        
        # Loại bỏ ký tự đặc biệt không cần thiết
        title = re.sub(r'\s+', ' ', title)  # Multiple spaces -> single space
        title = re.sub(r'[^\w\s\-\+\#\.\(\)/]', '', title)  # Keep only valid chars
        
        # Kiểm tra có phải spam không
        spam_patterns = [
            r'click here',
            r'apply now!!!',
            r'urgent!!!',
            r'\$\$\$',
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return False, None
        
        return True, title
    
    def validate_company(self, company: str) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra và làm sạch company name
        
        Returns:
            (is_valid, cleaned_company)
        """
        if not company or not isinstance(company, str):
            return False, None
        
        company = company.strip()
        
        # Kiểm tra độ dài
        if len(company) < 2:
            return False, None
        
        if len(company) > 150:
            company = company[:150]
        
        # Loại bỏ ký tự đặc biệt
        company = re.sub(r'\s+', ' ', company)
        
        # Chuẩn hóa tên công ty phổ biến
        company_mappings = {
            'FPT Software': ['FPT Soft', 'FPT SW', 'FPT-Software'],
            'VNG Corporation': ['VNG Corp', 'VNG Co'],
            'Viettel': ['Viettel Group', 'Tập đoàn Viettel'],
        }
        
        for standard_name, variants in company_mappings.items():
            for variant in variants:
                if variant.lower() in company.lower():
                    company = standard_name
                    break
        
        return True, company
    
    def validate_location(self, location: str) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra và chuẩn hóa location
        
        Returns:
            (is_valid, cleaned_location)
        """
        if not location or not isinstance(location, str):
            return True, 'Unknown'  # Location không bắt buộc
        
        location = location.strip()
        
        # Chuẩn hóa tên thành phố
        city_mappings = {
            'Hà Nội': ['Ha Noi', 'Hanoi', 'HN', 'Hà Nội'],
            'Hồ Chí Minh': ['Ho Chi Minh', 'HCM', 'HCMC', 'Sài Gòn', 'Saigon', 'TP.HCM'],
            'Đà Nẵng': ['Da Nang', 'Danang', 'DN'],
            'Cần Thơ': ['Can Tho', 'Cantho'],
            'Hải Phòng': ['Hai Phong', 'Haiphong'],
            'Biên Hòa': ['Bien Hoa', 'Bienhoa'],
            'Nha Trang': ['Nhatrang'],
            'Huế': ['Hue'],
        }
        
        for standard_name, variants in city_mappings.items():
            for variant in variants:
                if variant.lower() in location.lower():
                    return True, standard_name
        
        # Nếu không match, giữ nguyên nhưng clean
        location = re.sub(r'\s+', ' ', location)
        return True, location
    
    def validate_skills(self, skills: str) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra và làm sạch skills
        
        Returns:
            (is_valid, cleaned_skills)
        """
        if not skills or not isinstance(skills, str):
            return True, ''  # Skills không bắt buộc
        
        # Split và clean
        skills_list = [s.strip() for s in skills.split(',')]
        skills_list = [s for s in skills_list if s and len(s) > 1]
        
        # Loại bỏ duplicates (case-insensitive)
        seen = set()
        unique_skills = []
        for skill in skills_list:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        # Chuẩn hóa tên skill phổ biến
        skill_mappings = {
            'JavaScript': ['Javascript', 'JS', 'javascript'],
            'TypeScript': ['Typescript', 'TS'],
            'Python': ['python', 'PYTHON'],
            'Java': ['java', 'JAVA'],
            'C++': ['C Plus Plus', 'CPP'],
            'C#': ['C Sharp', 'CSharp'],
            'React': ['ReactJS', 'React.js'],
            'Angular': ['AngularJS', 'Angular.js'],
            'Vue': ['VueJS', 'Vue.js'],
            'Node.js': ['NodeJS', 'Node'],
            'SQL': ['sql', 'Sql'],
            'MySQL': ['mysql', 'My SQL'],
            'PostgreSQL': ['Postgres', 'postgres'],
            'MongoDB': ['Mongo', 'mongo'],
            'Docker': ['docker'],
            'Kubernetes': ['K8s', 'k8s'],
            'AWS': ['Amazon Web Services'],
            'Azure': ['Microsoft Azure'],
            'GCP': ['Google Cloud Platform', 'Google Cloud'],
        }
        
        standardized_skills = []
        for skill in unique_skills:
            standardized = skill
            for standard_name, variants in skill_mappings.items():
                if skill in variants or skill.lower() == standard_name.lower():
                    standardized = standard_name
                    break
            standardized_skills.append(standardized)
        
        cleaned_skills = ', '.join(standardized_skills)
        return True, cleaned_skills
    
    def validate_salary(
        self, 
        salary_min: Any, 
        salary_max: Any
    ) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Kiểm tra và làm sạch salary
        
        Returns:
            (is_valid, cleaned_min, cleaned_max)
        """
        def clean_salary_value(value: Any) -> Optional[float]:
            if value is None or value == '':
                return None
            
            try:
                # Convert to float
                if isinstance(value, str):
                    # Remove currency symbols and commas
                    value = re.sub(r'[^\d.]', '', value)
                
                salary = float(value)
                
                # Validate range (VND in millions)
                if salary < 0:
                    return None
                
                # Reasonable salary range: 1M - 500M VND
                if salary > 500:
                    return None
                
                return salary
                
            except (ValueError, TypeError):
                return None
        
        min_salary = clean_salary_value(salary_min)
        max_salary = clean_salary_value(salary_max)
        
        # Validate min <= max
        if min_salary and max_salary and min_salary > max_salary:
            # Swap them
            min_salary, max_salary = max_salary, min_salary
        
        return True, min_salary, max_salary
    
    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra và làm sạch URL
        
        Returns:
            (is_valid, cleaned_url)
        """
        if not url or not isinstance(url, str):
            return True, ''  # URL không bắt buộc
        
        url = url.strip()
        
        # Kiểm tra format URL cơ bản
        url_pattern = r'^https?://'
        if not re.match(url_pattern, url):
            # Thêm https:// nếu thiếu
            if not url.startswith('//'):
                url = 'https://' + url
            else:
                url = 'https:' + url
        
        # Validate domain
        if not re.search(r'\.[a-z]{2,}', url, re.IGNORECASE):
            return False, None
        
        return True, url
    
    def validate_job_level(self, job_level: str) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra và chuẩn hóa job level
        
        Returns:
            (is_valid, cleaned_level)
        """
        if not job_level or not isinstance(job_level, str):
            return True, 'Not Specified'
        
        job_level = job_level.strip()
        
        # Chuẩn hóa job levels
        level_mappings = {
            'Intern': ['Internship', 'Thực tập sinh', 'Thực tập'],
            'Fresher': ['Entry Level', 'Junior', 'Mới tốt nghiệp'],
            'Junior': ['Junior Level'],
            'Middle': ['Mid Level', 'Middle Level', 'Experienced'],
            'Senior': ['Senior Level', 'Expert'],
            'Lead': ['Team Lead', 'Tech Lead', 'Leader'],
            'Manager': ['Project Manager', 'Engineering Manager', 'Quản lý'],
            'Director': ['Director Level', 'Head of'],
        }
        
        for standard_level, variants in level_mappings.items():
            if job_level in variants or job_level.lower() == standard_level.lower():
                return True, standard_level
            for variant in variants:
                if variant.lower() in job_level.lower():
                    return True, standard_level
        
        return True, job_level
    
    # ========================================================================
    # QUALITY SCORING - Đánh giá chất lượng
    # ========================================================================
    
    def calculate_quality_score(self, job: Dict[str, Any]) -> Tuple[int, DataQuality]:
        """
        Tính điểm chất lượng cho job (0-100)
        
        Returns:
            (score, quality_level)
        """
        score = 0
        
        # Required fields (40 points)
        if job.get('title') and str(job['title']).strip():
            score += 20
        if job.get('company') and str(job['company']).strip():
            score += 20
        
        # Important fields (40 points)
        if job.get('location') and str(job['location']).strip() != 'Unknown':
            score += 10
        if job.get('skills') and str(job['skills']).strip():
            score += 15
        if job.get('job_level') and str(job['job_level']).strip() != 'Not Specified':
            score += 10
        if job.get('url') and str(job['url']).strip():
            score += 5
        
        # Nice-to-have fields (20 points)
        if job.get('salary_min') or job.get('salary_max'):
            score += 10
        if job.get('description') and len(str(job.get('description', ''))) > 50:
            score += 5
        if job.get('requirements') and len(str(job.get('requirements', ''))) > 50:
            score += 5
        
        # Determine quality level
        if score >= 90:
            quality = DataQuality.EXCELLENT
        elif score >= 75:
            quality = DataQuality.GOOD
        elif score >= 60:
            quality = DataQuality.ACCEPTABLE
        elif score >= 40:
            quality = DataQuality.POOR
        else:
            quality = DataQuality.BAD
        
        return score, quality
    
    # ========================================================================
    # MAIN VALIDATION & CLEANING
    # ========================================================================
    
    def validate_and_clean_job(
        self, 
        job: Dict[str, Any],
        reject_poor_quality: bool = True
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Kiểm tra và làm sạch một job
        
        Args:
            job: Job data
            reject_poor_quality: Từ chối job có chất lượng kém
        
        Returns:
            (is_valid, cleaned_job, errors)
        """
        errors = []
        cleaned_job = job.copy()
        
        # 1. Validate required fields
        is_valid, missing_fields = self.validate_required_fields(job)
        if not is_valid:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            return False, None, errors
        
        # 2. Validate and clean title
        is_valid, cleaned_title = self.validate_title(job.get('title', ''))
        if not is_valid:
            errors.append("Invalid title")
            return False, None, errors
        cleaned_job['title'] = cleaned_title
        
        # 3. Validate and clean company
        is_valid, cleaned_company = self.validate_company(job.get('company', ''))
        if not is_valid:
            errors.append("Invalid company")
            return False, None, errors
        cleaned_job['company'] = cleaned_company
        
        # 4. Validate and clean location
        is_valid, cleaned_location = self.validate_location(job.get('location', ''))
        cleaned_job['location'] = cleaned_location
        
        # 5. Validate and clean skills
        is_valid, cleaned_skills = self.validate_skills(job.get('skills', ''))
        cleaned_job['skills'] = cleaned_skills
        
        # 6. Validate and clean salary
        is_valid, min_sal, max_sal = self.validate_salary(
            job.get('salary_min'), 
            job.get('salary_max')
        )
        cleaned_job['salary_min'] = min_sal
        cleaned_job['salary_max'] = max_sal
        
        # 7. Validate and clean URL
        is_valid, cleaned_url = self.validate_url(job.get('url', ''))
        cleaned_job['url'] = cleaned_url
        
        # 8. Validate and clean job level
        is_valid, cleaned_level = self.validate_job_level(job.get('job_level', ''))
        cleaned_job['job_level'] = cleaned_level
        
        # 9. Calculate quality score
        score, quality = self.calculate_quality_score(cleaned_job)
        cleaned_job['quality_score'] = score
        cleaned_job['quality_level'] = quality.name
        
        # 10. Reject poor quality if needed
        if reject_poor_quality and quality == DataQuality.BAD:
            errors.append(f"Poor quality job (score: {score})")
            return False, None, errors
        
        return True, cleaned_job, errors
    
    def validate_and_clean_batch(
        self,
        jobs: List[Dict[str, Any]],
        reject_poor_quality: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Kiểm tra và làm sạch một batch jobs
        
        Returns:
            (valid_jobs, invalid_jobs)
        """
        valid_jobs = []
        invalid_jobs = []
        
        self.validation_stats['total_jobs'] = len(jobs)
        
        for job in jobs:
            is_valid, cleaned_job, errors = self.validate_and_clean_job(
                job, 
                reject_poor_quality
            )
            
            if is_valid and cleaned_job:
                valid_jobs.append(cleaned_job)
                self.validation_stats['valid_jobs'] += 1
                self.validation_stats['quality_scores'].append(
                    cleaned_job.get('quality_score', 0)
                )
            else:
                invalid_jobs.append({
                    'job': job,
                    'errors': errors
                })
                self.validation_stats['invalid_jobs'] += 1
        
        return valid_jobs, invalid_jobs
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê validation"""
        stats = self.validation_stats.copy()
        
        if stats['quality_scores']:
            stats['avg_quality_score'] = sum(stats['quality_scores']) / len(stats['quality_scores'])
            stats['min_quality_score'] = min(stats['quality_scores'])
            stats['max_quality_score'] = max(stats['quality_scores'])
        
        return stats
    
    def print_stats(self):
        """In thống kê chi tiết"""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("DATA VALIDATION STATISTICS")
        print("="*60)
        print(f"Total jobs processed:    {stats['total_jobs']:,}")
        print(f"Valid jobs:              {stats['valid_jobs']:,}")
        print(f"Invalid jobs:            {stats['invalid_jobs']:,}")
        print(f"Validation rate:         {stats['valid_jobs']/stats['total_jobs']*100:.1f}%")
        
        if 'avg_quality_score' in stats:
            print("-"*60)
            print(f"Average quality score:   {stats['avg_quality_score']:.1f}")
            print(f"Min quality score:       {stats['min_quality_score']:.1f}")
            print(f"Max quality score:       {stats['max_quality_score']:.1f}")
        
        print("="*60)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == '__main__':
    validator = DataValidator()
    
    # Example jobs with various quality levels
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'FPT Software',
            'location': 'Ha Noi',
            'skills': 'Python, Django, PostgreSQL',
            'job_level': 'Senior',
            'salary_min': 20,
            'salary_max': 35,
            'url': 'https://example.com/job/1'
        },
        {
            'title': 'Dev',  # Too short
            'company': 'X',  # Too short
            'location': '',
            'skills': '',
            'job_level': '',
        },
        {
            'title': 'Java Developer',
            'company': 'VNG Corp',
            'location': 'HCM',
            'skills': 'java, JAVA, Java, Spring',  # Duplicates
            'job_level': 'middle',
        },
    ]
    
    # Validate and clean
    valid_jobs, invalid_jobs = validator.validate_and_clean_batch(
        sample_jobs,
        reject_poor_quality=True
    )
    
    print(f"\nValid jobs: {len(valid_jobs)}")
    for job in valid_jobs:
        print(f"  - {job['title']} at {job['company']} (Score: {job['quality_score']})")
    
    print(f"\nInvalid jobs: {len(invalid_jobs)}")
    for item in invalid_jobs:
        print(f"  - Errors: {', '.join(item['errors'])}")
    
    validator.print_stats()
