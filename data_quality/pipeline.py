"""
INTEGRATED DATA QUALITY PIPELINE
Kết hợp deduplication và validation thành một pipeline hoàn chỉnh
"""

import sqlite3
from typing import Dict, Any, List, Tuple
from datetime import datetime
import pandas as pd

from deduplication import DeduplicationEngine
from data_validation import DataValidator, DataQuality


class DataQualityPipeline:
    """
    Pipeline xử lý chất lượng dữ liệu hoàn chỉnh
    
    Workflow:
    1. Load data
    2. Validate & Clean (xử lý dữ liệu xấu)
    3. Deduplicate (xử lý trùng lặp)
    4. Quality scoring
    5. Save results
    """
    
    def __init__(self, db_path: str = '../it_jobs_vietnam.db'):
        self.db_path = db_path
        self.validator = DataValidator(db_path)
        self.deduplicator = DeduplicationEngine(db_path)
        
        self.pipeline_stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'input_count': 0,
            'output_count': 0,
            'removed_count': 0,
            'removal_rate': 0.0
        }
    
    def process_jobs(
        self,
        jobs: List[Dict[str, Any]],
        validate: bool = True,
        deduplicate: bool = True,
        reject_poor_quality: bool = True,
        use_fuzzy_dedup: bool = False
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Xử lý một batch jobs qua pipeline
        
        Args:
            jobs: Danh sách jobs cần xử lý
            validate: Có validate và clean không
            deduplicate: Có deduplicate không
            reject_poor_quality: Từ chối jobs chất lượng kém
            use_fuzzy_dedup: Sử dụng fuzzy deduplication (chậm)
        
        Returns:
            (processed_jobs, stats)
        """
        self.pipeline_stats['start_time'] = datetime.now()
        self.pipeline_stats['input_count'] = len(jobs)
        
        print("\n" + "="*70)
        print("DATA QUALITY PIPELINE STARTED")
        print("="*70)
        print(f"Input: {len(jobs):,} jobs")
        print(f"Timestamp: {self.pipeline_stats['start_time']}")
        print("="*70)
        
        processed_jobs = jobs
        
        # STEP 1: Validation & Cleaning
        if validate:
            print("\n[STEP 1/2] VALIDATION & CLEANING")
            print("-"*70)
            
            valid_jobs, invalid_jobs = self.validator.validate_and_clean_batch(
                processed_jobs,
                reject_poor_quality=reject_poor_quality
            )
            
            print(f"✓ Valid jobs: {len(valid_jobs):,}")
            print(f"✗ Invalid jobs: {len(invalid_jobs):,}")
            
            if invalid_jobs:
                print(f"\nSample invalid jobs:")
                for i, item in enumerate(invalid_jobs[:3]):
                    print(f"  {i+1}. Errors: {', '.join(item['errors'])}")
            
            processed_jobs = valid_jobs
        
        # STEP 2: Deduplication
        if deduplicate:
            print("\n[STEP 2/2] DEDUPLICATION")
            print("-"*70)
            
            processed_jobs = self.deduplicator.deduplicate_all(
                processed_jobs,
                use_exact=True,
                use_url=True,
                use_fuzzy=use_fuzzy_dedup,
                use_content=False,
                fuzzy_threshold=0.85
            )
            
            print(f"✓ Unique jobs: {len(processed_jobs):,}")
        
        # Calculate final stats
        self.pipeline_stats['end_time'] = datetime.now()
        self.pipeline_stats['output_count'] = len(processed_jobs)
        self.pipeline_stats['removed_count'] = (
            self.pipeline_stats['input_count'] - self.pipeline_stats['output_count']
        )
        self.pipeline_stats['removal_rate'] = (
            self.pipeline_stats['removed_count'] / self.pipeline_stats['input_count'] * 100
            if self.pipeline_stats['input_count'] > 0 else 0
        )
        self.pipeline_stats['duration_seconds'] = (
            self.pipeline_stats['end_time'] - self.pipeline_stats['start_time']
        ).total_seconds()
        
        # Print summary
        self._print_summary()
        
        # Combine stats
        combined_stats = {
            'pipeline': self.pipeline_stats,
            'validation': self.validator.get_stats() if validate else {},
            'deduplication': self.deduplicator.get_stats() if deduplicate else {}
        }
        
        return processed_jobs, combined_stats
    
    def process_from_csv(
        self,
        input_csv: str,
        output_csv: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Xử lý jobs từ CSV file
        
        Args:
            input_csv: Đường dẫn file CSV input
            output_csv: Đường dẫn file CSV output
            **kwargs: Các tham số cho process_jobs()
        
        Returns:
            stats dictionary
        """
        print(f"\nLoading data from: {input_csv}")
        df = pd.read_csv(input_csv)
        jobs = df.to_dict('records')
        
        processed_jobs, stats = self.process_jobs(jobs, **kwargs)
        
        # Save to CSV
        if processed_jobs:
            df_output = pd.DataFrame(processed_jobs)
            df_output.to_csv(output_csv, index=False, encoding='utf-8-sig')
            print(f"\n✓ Saved {len(processed_jobs):,} jobs to: {output_csv}")
        
        return stats
    
    def process_from_database(
        self,
        input_table: str = 'jobs_realtime',
        output_table: str = 'jobs_cleaned',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Xử lý jobs từ database
        
        Args:
            input_table: Tên bảng input
            output_table: Tên bảng output
            **kwargs: Các tham số cho process_jobs()
        
        Returns:
            stats dictionary
        """
        conn = sqlite3.connect(self.db_path)
        
        print(f"\nLoading data from table: {input_table}")
        df = pd.read_sql_query(f"SELECT * FROM {input_table}", conn)
        jobs = df.to_dict('records')
        
        processed_jobs, stats = self.process_jobs(jobs, **kwargs)
        
        # Save to database
        if processed_jobs:
            df_output = pd.DataFrame(processed_jobs)
            df_output.to_sql(output_table, conn, if_exists='replace', index=False)
            print(f"\n✓ Saved {len(processed_jobs):,} jobs to table: {output_table}")
        
        conn.close()
        
        return stats
    
    def _print_summary(self):
        """In tóm tắt kết quả pipeline"""
        print("\n" + "="*70)
        print("PIPELINE SUMMARY")
        print("="*70)
        print(f"Input jobs:              {self.pipeline_stats['input_count']:,}")
        print(f"Output jobs:             {self.pipeline_stats['output_count']:,}")
        print(f"Removed jobs:            {self.pipeline_stats['removed_count']:,}")
        print(f"Removal rate:            {self.pipeline_stats['removal_rate']:.2f}%")
        print(f"Processing time:         {self.pipeline_stats['duration_seconds']:.2f}s")
        print(f"Throughput:              {self.pipeline_stats['input_count']/self.pipeline_stats['duration_seconds']:.0f} jobs/sec")
        print("="*70)
    
    def get_quality_report(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Tạo báo cáo chất lượng chi tiết
        
        Returns:
            Quality report dictionary
        """
        if not jobs:
            return {}
        
        df = pd.DataFrame(jobs)
        
        report = {
            'total_jobs': len(jobs),
            'completeness': {},
            'quality_distribution': {},
            'field_statistics': {}
        }
        
        # Completeness analysis
        for col in df.columns:
            non_null = df[col].notna().sum()
            non_empty = (df[col].astype(str).str.strip() != '').sum()
            report['completeness'][col] = {
                'non_null': int(non_null),
                'non_empty': int(non_empty),
                'completeness_rate': round(non_empty / len(df) * 100, 2)
            }
        
        # Quality score distribution
        if 'quality_score' in df.columns:
            report['quality_distribution'] = {
                'mean': round(df['quality_score'].mean(), 2),
                'median': round(df['quality_score'].median(), 2),
                'min': round(df['quality_score'].min(), 2),
                'max': round(df['quality_score'].max(), 2),
                'std': round(df['quality_score'].std(), 2)
            }
        
        # Field statistics
        if 'skills' in df.columns:
            skill_counts = df['skills'].str.split(',').str.len()
            report['field_statistics']['avg_skills_per_job'] = round(skill_counts.mean(), 2)
        
        if 'location' in df.columns:
            report['field_statistics']['unique_locations'] = int(df['location'].nunique())
        
        if 'company' in df.columns:
            report['field_statistics']['unique_companies'] = int(df['company'].nunique())
        
        return report
    
    def print_quality_report(self, jobs: List[Dict[str, Any]]):
        """In báo cáo chất lượng"""
        report = self.get_quality_report(jobs)
        
        print("\n" + "="*70)
        print("DATA QUALITY REPORT")
        print("="*70)
        
        print(f"\nTotal jobs: {report['total_jobs']:,}")
        
        print("\nField Completeness:")
        for field, stats in report['completeness'].items():
            print(f"  {field:20s}: {stats['completeness_rate']:6.2f}% ({stats['non_empty']:,}/{report['total_jobs']:,})")
        
        if report['quality_distribution']:
            print("\nQuality Score Distribution:")
            for metric, value in report['quality_distribution'].items():
                print(f"  {metric:10s}: {value:.2f}")
        
        if report['field_statistics']:
            print("\nField Statistics:")
            for metric, value in report['field_statistics'].items():
                print(f"  {metric:30s}: {value}")
        
        print("="*70)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == '__main__':
    # Example 1: Process from CSV
    print("="*70)
    print("EXAMPLE 1: Process from CSV")
    print("="*70)
    
    pipeline = DataQualityPipeline()
    
    try:
        stats = pipeline.process_from_csv(
            input_csv='../crawler/it_jobs_vietnam.csv',
            output_csv='../clean_it_jobs.csv',
            validate=True,
            deduplicate=True,
            reject_poor_quality=True,
            use_fuzzy_dedup=False  # Set True for better dedup but slower
        )
        
        print("\n✓ Pipeline completed successfully!")
        
    except FileNotFoundError:
        print("\n✗ Input file not found. Please run crawler first.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # Example 2: Process from database
    print("\n\n" + "="*70)
    print("EXAMPLE 2: Process from Database")
    print("="*70)
    
    pipeline2 = DataQualityPipeline()
    
    try:
        stats = pipeline2.process_from_database(
            input_table='jobs_realtime',
            output_table='jobs_cleaned',
            validate=True,
            deduplicate=True,
            reject_poor_quality=False,  # Keep all jobs
            use_fuzzy_dedup=False
        )
        
        print("\n✓ Database processing completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # Example 3: Quality report
    print("\n\n" + "="*70)
    print("EXAMPLE 3: Generate Quality Report")
    print("="*70)
    
    try:
        import pandas as pd
        df = pd.read_csv('../clean_it_jobs.csv')
        jobs = df.to_dict('records')
        
        pipeline3 = DataQualityPipeline()
        pipeline3.print_quality_report(jobs)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
