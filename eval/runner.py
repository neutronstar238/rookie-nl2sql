"""
Benchmark runner script for NL2SQL evaluation.
M10: Execute benchmarks and generate reports.
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eval.benchmark import BenchmarkRunner
from eval.test_cases import (
    get_all_test_cases,
    get_test_cases_by_category
)


def run_full_benchmark(output_dir: str = "eval/reports"):
    """Run full benchmark suite"""
    print("\n" + "="*70)
    print("NL2SQL Full Benchmark Suite")
    print("="*70)
    
    # Get all test cases
    test_cases = get_all_test_cases()
    
    print(f"\nTotal test cases: {len(test_cases)}")
    
    # Run benchmark
    runner = BenchmarkRunner()
    report = runner.run_benchmark(test_cases)
    
    # Print report
    runner.print_report(report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}/benchmark_full_{timestamp}.json"
    runner.save_report(report, output_path)
    
    return report


def run_category_benchmark(category: str, output_dir: str = "eval/reports"):
    """Run benchmark for specific category"""
    print("\n" + "="*70)
    print(f"NL2SQL Benchmark - Category: {category}")
    print("="*70)
    
    # Get test cases for category
    test_cases = get_test_cases_by_category(category)
    
    if not test_cases:
        print(f"\n✗ No test cases found for category: {category}")
        return None
    
    print(f"\nTest cases in category: {len(test_cases)}")
    
    # Run benchmark
    runner = BenchmarkRunner()
    report = runner.run_benchmark(test_cases)
    
    # Print report
    runner.print_report(report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}/benchmark_{category}_{timestamp}.json"
    runner.save_report(report, output_path)
    
    return report


def run_quick_test(num_cases: int = 5, output_dir: str = "eval/reports"):
    """Run quick test with limited cases"""
    print("\n" + "="*70)
    print(f"NL2SQL Quick Test - {num_cases} cases")
    print("="*70)
    
    # Get first N test cases
    all_cases = get_all_test_cases()
    test_cases = all_cases[:num_cases]
    
    print(f"\nRunning {len(test_cases)} test cases")
    
    # Run benchmark
    runner = BenchmarkRunner()
    report = runner.run_benchmark(test_cases)
    
    # Print report
    runner.print_report(report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}/benchmark_quick_{timestamp}.json"
    runner.save_report(report, output_path)
    
    return report


def compare_reports(report_paths: list):
    """Compare multiple benchmark reports"""
    import json
    
    print("\n" + "="*70)
    print("Benchmark Comparison")
    print("="*70)
    
    reports = []
    for path in report_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                report = json.load(f)
                reports.append({
                    "path": path,
                    "data": report
                })
        except Exception as e:
            print(f"✗ Failed to load {path}: {e}")
    
    if len(reports) < 2:
        print("\n✗ Need at least 2 reports to compare")
        return
    
    print(f"\nComparing {len(reports)} reports:\n")
    
    # Print comparison table
    print(f"{'Metric':<30} | " + " | ".join([f"Report {i+1:>8}" for i in range(len(reports))]))
    print("-" * 70)
    
    metrics = [
        ("Total Cases", lambda r: r['summary']['total_cases']),
        ("Exact Match %", lambda r: r['summary']['metrics']['sql_exact_match_rate']),
        ("Semantic Match %", lambda r: r['summary']['metrics']['sql_semantic_match_rate']),
        ("Execution Success %", lambda r: r['summary']['metrics']['execution_success_rate']),
        ("Avg Time (s)", lambda r: r['summary']['avg_time_per_case'])
    ]
    
    for metric_name, metric_fn in metrics:
        values = []
        for report in reports:
            try:
                value = metric_fn(report['data'])
                values.append(value)
            except:
                values.append("N/A")
        
        values_str = " | ".join([f"{v:>10}" for v in values])
        print(f"{metric_name:<30} | {values_str}")
    
    print("\n" + "="*70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NL2SQL Benchmark Runner")
    parser.add_argument(
        "mode",
        choices=["full", "category", "quick", "compare"],
        help="Benchmark mode"
    )
    parser.add_argument(
        "--category",
        help="Category name (for category mode)"
    )
    parser.add_argument(
        "--num-cases",
        type=int,
        default=5,
        help="Number of cases for quick test (default: 5)"
    )
    parser.add_argument(
        "--output-dir",
        default="eval/reports",
        help="Output directory for reports (default: eval/reports)"
    )
    parser.add_argument(
        "--reports",
        nargs="+",
        help="Report paths to compare (for compare mode)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        run_full_benchmark(args.output_dir)
    
    elif args.mode == "category":
        if not args.category:
            print("✗ --category required for category mode")
            sys.exit(1)
        run_category_benchmark(args.category, args.output_dir)
    
    elif args.mode == "quick":
        run_quick_test(args.num_cases, args.output_dir)
    
    elif args.mode == "compare":
        if not args.reports or len(args.reports) < 2:
            print("✗ --reports required with at least 2 paths for compare mode")
            sys.exit(1)
        compare_reports(args.reports)


if __name__ == "__main__":
    # If no args, run quick test
    if len(sys.argv) == 1:
        print("Running quick test (use --help for more options)")
        run_quick_test(num_cases=5)
    else:
        main()
