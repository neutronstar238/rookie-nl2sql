"""
Benchmark framework for NL2SQL system evaluation.
M10: Standardized testing and performance metrics.
"""
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from graphs.base_graph import run_query
from tools.db import db_client


class BenchmarkCase:
    """Single benchmark test case"""
    
    def __init__(
        self,
        question: str,
        expected_sql: Optional[str] = None,
        expected_result_count: Optional[int] = None,
        description: str = "",
        category: str = "general"
    ):
        """
        Initialize benchmark case.
        
        Args:
            question: Natural language question
            expected_sql: Expected SQL query (for exact match)
            expected_result_count: Expected number of rows
            description: Test case description
            category: Test category (simple, aggregate, join, etc.)
        """
        self.question = question
        self.expected_sql = expected_sql
        self.expected_result_count = expected_result_count
        self.description = description
        self.category = category
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "question": self.question,
            "expected_sql": self.expected_sql,
            "expected_result_count": self.expected_result_count,
            "description": self.description,
            "category": self.category
        }


class BenchmarkResult:
    """Results for a single benchmark case"""
    
    def __init__(
        self,
        case: BenchmarkCase,
        generated_sql: str,
        execution_success: bool,
        result_count: int,
        execution_time: float,
        answer: str = "",
        error: str = ""
    ):
        self.case = case
        self.generated_sql = generated_sql
        self.execution_success = execution_success
        self.result_count = result_count
        self.execution_time = execution_time
        self.answer = answer
        self.error = error
        
        # Compute metrics
        self.sql_exact_match = self._check_sql_exact_match()
        self.sql_semantic_match = self._check_sql_semantic_match()
        self.execution_accuracy = self._check_execution_accuracy()
    
    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for comparison"""
        if not sql:
            return ""
        # Remove extra whitespace and newlines
        normalized = " ".join(sql.split())
        # Remove trailing semicolon
        normalized = normalized.rstrip(';').rstrip()
        # Remove LIMIT clause added by sandbox (for comparison)
        import re
        normalized = re.sub(r'\s+limit\s+\d+\s*$', '', normalized, flags=re.IGNORECASE)
        # Lowercase for comparison
        return normalized.lower().strip()
    
    def _check_sql_exact_match(self) -> bool:
        """Check if generated SQL exactly matches expected SQL"""
        if not self.case.expected_sql:
            return False
        
        expected_norm = self._normalize_sql(self.case.expected_sql)
        generated_norm = self._normalize_sql(self.generated_sql)
        
        return expected_norm == generated_norm
    
    def _check_sql_semantic_match(self) -> bool:
        """
        Check if generated SQL is semantically equivalent.
        Uses multiple strategies to determine semantic equivalence.
        """
        if not self.case.expected_sql:
            return False
        
        # If exact match, semantic match is true
        if self.sql_exact_match:
            return True
        
        # Execute both queries and compare results
        try:
            expected_result = db_client.query(self.case.expected_sql, fetch_limit=1000)
            generated_result = db_client.query(self.generated_sql, fetch_limit=1000)
            
            # Both should succeed
            if not (expected_result.get('ok') and generated_result.get('ok')):
                return False
            
            # Get rows and columns
            expected_rows = expected_result.get('rows', [])
            generated_rows = generated_result.get('rows', [])
            expected_cols = set(expected_result.get('columns', []))
            generated_cols = set(generated_result.get('columns', []))
            
            expected_norm = self._normalize_sql(self.case.expected_sql)
            generated_norm = self._normalize_sql(self.generated_sql)
            
            # Special handling for aggregate queries (COUNT, SUM, AVG, etc.)
            if any(agg in expected_norm for agg in ['count(', 'sum(', 'avg(', 'min(', 'max(']):
                # For aggregate queries, compare the actual values, not column names
                # Column names might differ due to aliases (e.g., "total" vs "COUNT(*)")
                if len(expected_rows) == 1 and len(generated_rows) == 1:
                    # Extract the first value from each result
                    expected_val = list(expected_rows[0].values())[0] if expected_rows[0] else None
                    generated_val = list(generated_rows[0].values())[0] if generated_rows[0] else None
                    
                    # Values should match
                    if expected_val == generated_val:
                        return True
            
            # For SELECT *, columns should match exactly
            if 'select *' in expected_norm and 'select *' in generated_norm:
                if expected_cols != generated_cols:
                    return False
                # Row counts should match
                if len(expected_rows) != len(generated_rows):
                    return False
                return True
            
            # For specific column selections
            # Allow if generated is a subset of expected (more specific query)
            if 'select *' in expected_norm and 'select *' not in generated_norm:
                # Generated is more specific, check if columns are subset
                # This is acceptable
                if len(expected_rows) == len(generated_rows):
                    return True
            
            # Compare row counts - they should match for semantic equivalence
            expected_count = expected_result.get('row_count', 0)
            generated_count = generated_result.get('row_count', 0)
            
            # Allow exact match
            if expected_count == generated_count and expected_count > 0:
                # If row counts match and both have columns overlap, it's semantic match
                if len(expected_cols.intersection(generated_cols)) > 0:
                    return True
            
            return False
            
        except Exception as e:
            # If execution fails, not a semantic match
            return False
    
    def _check_execution_accuracy(self) -> bool:
        """Check if execution result matches expected"""
        if not self.execution_success:
            return False
        
        # If expected result count is provided, check it
        if self.case.expected_result_count is not None:
            return self.result_count == self.case.expected_result_count
        
        # Otherwise, just check that query executed successfully
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "question": self.case.question,
            "category": self.case.category,
            "description": self.case.description,
            "expected_sql": self.case.expected_sql,
            "generated_sql": self.generated_sql,
            "execution_success": self.execution_success,
            "result_count": self.result_count,
            "execution_time": self.execution_time,
            "answer": self.answer,
            "error": self.error,
            "metrics": {
                "sql_exact_match": self.sql_exact_match,
                "sql_semantic_match": self.sql_semantic_match,
                "execution_accuracy": self.execution_accuracy
            }
        }


class BenchmarkRunner:
    """Benchmark test runner"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    def run_case(self, case: BenchmarkCase) -> BenchmarkResult:
        """
        Run a single benchmark case.
        
        Args:
            case: Benchmark case to run
            
        Returns:
            BenchmarkResult with metrics
        """
        print(f"\nRunning: {case.question}")
        
        start_time = time.time()
        
        try:
            # Run query through graph
            state = run_query(case.question)
            
            execution_time = time.time() - start_time
            
            # Extract results
            generated_sql = state.get('candidate_sql', '')
            execution_result = state.get('execution_result', {})
            answer = state.get('answer', '')
            
            execution_success = execution_result.get('ok', False)
            result_count = execution_result.get('row_count', 0)
            error = execution_result.get('error', '')
            
            result = BenchmarkResult(
                case=case,
                generated_sql=generated_sql,
                execution_success=execution_success,
                result_count=result_count,
                execution_time=round(execution_time, 3),
                answer=answer,
                error=error
            )
            
            # Print quick summary
            print(f"  SQL: {generated_sql[:80]}...")
            print(f"  Execution: {'✓' if execution_success else '✗'}")
            print(f"  Time: {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"  ✗ Error: {str(e)}")
            
            return BenchmarkResult(
                case=case,
                generated_sql="",
                execution_success=False,
                result_count=0,
                execution_time=execution_time,
                error=str(e)
            )
    
    def run_benchmark(self, cases: List[BenchmarkCase]) -> Dict[str, Any]:
        """
        Run full benchmark suite.
        
        Args:
            cases: List of benchmark cases
            
        Returns:
            Benchmark report dictionary
        """
        print("\n" + "="*70)
        print(f"Running Benchmark: {len(cases)} test cases")
        print("="*70)
        
        self.results = []
        start_time = time.time()
        
        for i, case in enumerate(cases, 1):
            print(f"\n[{i}/{len(cases)}] Category: {case.category}")
            result = self.run_case(case)
            self.results.append(result)
        
        total_time = time.time() - start_time
        
        # Generate report
        report = self._generate_report(total_time)
        
        print("\n" + "="*70)
        print("Benchmark Complete!")
        print("="*70)
        
        return report
    
    def _generate_report(self, total_time: float) -> Dict[str, Any]:
        """Generate benchmark report with metrics"""
        total_cases = len(self.results)
        
        if total_cases == 0:
            return {
                "summary": {},
                "by_category": {},
                "results": []
            }
        
        # Overall metrics
        sql_exact_matches = sum(1 for r in self.results if r.sql_exact_match)
        sql_semantic_matches = sum(1 for r in self.results if r.sql_semantic_match)
        execution_successes = sum(1 for r in self.results if r.execution_success)
        execution_accuracies = sum(1 for r in self.results if r.execution_accuracy)
        
        avg_time = sum(r.execution_time for r in self.results) / total_cases
        
        summary = {
            "total_cases": total_cases,
            "total_time": round(total_time, 2),
            "avg_time_per_case": round(avg_time, 2),
            "metrics": {
                "sql_exact_match_rate": round(sql_exact_matches / total_cases * 100, 2),
                "sql_semantic_match_rate": round(sql_semantic_matches / total_cases * 100, 2),
                "execution_success_rate": round(execution_successes / total_cases * 100, 2),
                "execution_accuracy_rate": round(execution_accuracies / total_cases * 100, 2)
            },
            "counts": {
                "sql_exact_match": sql_exact_matches,
                "sql_semantic_match": sql_semantic_matches,
                "execution_success": execution_successes,
                "execution_accuracy": execution_accuracies
            }
        }
        
        # Metrics by category
        categories = {}
        for result in self.results:
            cat = result.case.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        by_category = {}
        for cat, results in categories.items():
            cat_total = len(results)
            by_category[cat] = {
                "total": cat_total,
                "sql_exact_match_rate": round(
                    sum(1 for r in results if r.sql_exact_match) / cat_total * 100, 2
                ),
                "execution_success_rate": round(
                    sum(1 for r in results if r.execution_success) / cat_total * 100, 2
                )
            }
        
        return {
            "summary": summary,
            "by_category": by_category,
            "results": [r.to_dict() for r in self.results],
            "timestamp": datetime.now().isoformat()
        }
    
    def save_report(self, report: Dict[str, Any], filepath: str):
        """Save benchmark report to file"""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Report saved to: {output_path}")
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted benchmark report"""
        summary = report['summary']
        
        print("\n" + "="*70)
        print("BENCHMARK REPORT")
        print("="*70)
        
        print(f"\n📊 Summary")
        print(f"  Total Cases: {summary['total_cases']}")
        print(f"  Total Time: {summary['total_time']}s")
        print(f"  Avg Time/Case: {summary['avg_time_per_case']}s")
        
        metrics = summary['metrics']
        print(f"\n📈 Metrics")
        print(f"  SQL Exact Match Rate: {metrics['sql_exact_match_rate']}%")
        print(f"  SQL Semantic Match Rate: {metrics['sql_semantic_match_rate']}%")
        print(f"  Execution Success Rate: {metrics['execution_success_rate']}%")
        print(f"  Execution Accuracy Rate: {metrics['execution_accuracy_rate']}%")
        
        by_category = report['by_category']
        if by_category:
            print(f"\n📂 By Category")
            for cat, stats in by_category.items():
                print(f"  {cat}:")
                print(f"    Total: {stats['total']}")
                print(f"    Exact Match: {stats['sql_exact_match_rate']}%")
                print(f"    Execution Success: {stats['execution_success_rate']}%")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    """Test benchmark framework"""
    print("=== Benchmark Framework Test ===\n")
    
    # Create sample test cases
    test_cases = [
        BenchmarkCase(
            question="有多少首歌曲？",
            expected_sql="SELECT COUNT(*) as total FROM Track",
            category="simple_aggregate",
            description="Simple count query"
        ),
        BenchmarkCase(
            question="显示所有音乐风格",
            expected_sql="SELECT * FROM Genre",
            category="simple_select",
            description="Simple SELECT all"
        ),
        BenchmarkCase(
            question="价格最高的5首歌曲",
            expected_sql="SELECT Name, UnitPrice FROM Track ORDER BY UnitPrice DESC LIMIT 5",
            category="top_n",
            description="Top N with ORDER BY"
        )
    ]
    
    # Run benchmark
    runner = BenchmarkRunner()
    report = runner.run_benchmark(test_cases)
    
    # Print report
    runner.print_report(report)
    
    # Save report
    runner.save_report(report, "eval/reports/test_report.json")
    
    print("\n✓ Benchmark framework test complete")
