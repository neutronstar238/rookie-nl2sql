"""
M10 Acceptance Tests: Benchmark Framework
Tests the evaluation and benchmarking system.
"""
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eval.benchmark import BenchmarkRunner, BenchmarkCase
from eval.test_cases import get_all_test_cases, get_test_cases_by_category
from eval.report_generator import ReportGenerator


def test_benchmark_framework():
    """Test that benchmark framework works correctly"""
    print("\n" + "="*70)
    print("M10 Acceptance Test: Benchmark Framework")
    print("="*70 + "\n")
    
    # Create simple test cases
    test_cases = [
        BenchmarkCase(
            question="有多少首歌曲？",
            expected_sql="SELECT COUNT(*) as total FROM Track",
            category="test_aggregate"
        ),
        BenchmarkCase(
            question="显示所有音乐风格",
            expected_sql="SELECT * FROM Genre",
            category="test_select"
        )
    ]
    
    print(f"Running benchmark with {len(test_cases)} test cases...")
    
    try:
        runner = BenchmarkRunner()
        report = runner.run_benchmark(test_cases)
        
        # Verify report structure
        assert 'summary' in report, "Report missing 'summary'"
        assert 'by_category' in report, "Report missing 'by_category'"
        assert 'results' in report, "Report missing 'results'"
        assert 'timestamp' in report, "Report missing 'timestamp'"
        
        # Verify summary
        summary = report['summary']
        assert summary['total_cases'] == len(test_cases), "Incorrect total_cases"
        assert 'metrics' in summary, "Summary missing metrics"
        assert 'total_time' in summary, "Summary missing total_time"
        
        # Verify metrics exist
        metrics = summary['metrics']
        required_metrics = [
            'sql_exact_match_rate',
            'sql_semantic_match_rate',
            'execution_success_rate',
            'execution_accuracy_rate'
        ]
        for metric in required_metrics:
            assert metric in metrics, f"Missing metric: {metric}"
        
        # Verify results
        assert len(report['results']) == len(test_cases), "Incorrect number of results"
        
        print("\n✓ PASSED - Benchmark framework structure correct")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_test_case_loading():
    """Test that test cases can be loaded"""
    print("\n" + "="*70)
    print("M10 Acceptance Test: Test Case Loading")
    print("="*70 + "\n")
    
    try:
        # Load all test cases
        all_cases = get_all_test_cases()
        
        assert len(all_cases) > 0, "No test cases loaded"
        print(f"✓ Loaded {len(all_cases)} test cases")
        
        # Verify case structure
        for case in all_cases[:3]:
            assert hasattr(case, 'question'), "Case missing question"
            assert hasattr(case, 'category'), "Case missing category"
            assert case.question, "Question is empty"
            assert case.category, "Category is empty"
        
        print("✓ Test case structure valid")
        
        # Test category loading
        categories = ['simple_select', 'aggregate', 'filter']
        for category in categories:
            cases = get_test_cases_by_category(category)
            print(f"✓ Category '{category}': {len(cases)} cases")
        
        print("\n✓ PASSED - Test case loading works correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_calculation():
    """Test that metrics are calculated correctly"""
    print("\n" + "="*70)
    print("M10 Acceptance Test: Metrics Calculation")
    print("="*70 + "\n")
    
    try:
        # Create controlled test cases
        test_cases = [
            BenchmarkCase(
                question="统计歌曲数量",
                expected_sql="SELECT COUNT(*) as total FROM Track",
                expected_result_count=1,
                category="test"
            )
        ]
        
        runner = BenchmarkRunner()
        report = runner.run_benchmark(test_cases)
        
        metrics = report['summary']['metrics']
        
        # Verify metric ranges
        for metric_name, value in metrics.items():
            assert 0 <= value <= 100, f"{metric_name} out of range: {value}"
            print(f"✓ {metric_name}: {value}%")
        
        print("\n✓ PASSED - Metrics calculation correct")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generation():
    """Test that reports can be generated and saved"""
    print("\n" + "="*70)
    print("M10 Acceptance Test: Report Generation")
    print("="*70 + "\n")
    
    try:
        # Create sample test
        test_cases = [
            BenchmarkCase(
                question="测试问题",
                expected_sql="SELECT * FROM Track LIMIT 5",
                category="test"
            )
        ]
        
        runner = BenchmarkRunner()
        report = runner.run_benchmark(test_cases)
        
        # Test JSON saving
        json_path = "eval/reports/test_acceptance.json"
        runner.save_report(report, json_path)
        
        # Verify file exists
        assert Path(json_path).exists(), "JSON report not saved"
        print(f"✓ JSON report saved: {json_path}")
        
        # Verify JSON is valid
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded_report = json.load(f)
        assert loaded_report['summary']['total_cases'] == 1
        print("✓ JSON report valid")
        
        # Test Markdown generation
        md_path = "eval/reports/test_acceptance.md"
        generator = ReportGenerator()
        generator.generate_markdown(report, md_path)
        
        assert Path(md_path).exists(), "Markdown report not saved"
        print(f"✓ Markdown report saved: {md_path}")
        
        # Test HTML generation
        html_path = "eval/reports/test_acceptance.html"
        generator.generate_html(report, html_path)
        
        assert Path(html_path).exists(), "HTML report not saved"
        print(f"✓ HTML report saved: {html_path}")
        
        print("\n✓ PASSED - Report generation works correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_category_breakdown():
    """Test that results are correctly broken down by category"""
    print("\n" + "="*70)
    print("M10 Acceptance Test: Category Breakdown")
    print("="*70 + "\n")
    
    try:
        # Create multi-category test cases
        test_cases = [
            BenchmarkCase(question="Q1", expected_sql="SELECT 1", category="cat1"),
            BenchmarkCase(question="Q2", expected_sql="SELECT 2", category="cat1"),
            BenchmarkCase(question="Q3", expected_sql="SELECT 3", category="cat2"),
        ]
        
        runner = BenchmarkRunner()
        report = runner.run_benchmark(test_cases)
        
        by_category = report['by_category']
        
        # Verify categories exist
        assert 'cat1' in by_category, "Category 'cat1' missing"
        assert 'cat2' in by_category, "Category 'cat2' missing"
        
        # Verify counts
        assert by_category['cat1']['total'] == 2, "cat1 count incorrect"
        assert by_category['cat2']['total'] == 1, "cat2 count incorrect"
        
        print("✓ Category counts correct")
        print(f"  cat1: {by_category['cat1']['total']} cases")
        print(f"  cat2: {by_category['cat2']['total']} cases")
        
        # Verify each category has metrics
        for cat, stats in by_category.items():
            assert 'sql_exact_match_rate' in stats
            assert 'execution_success_rate' in stats
            print(f"✓ Category '{cat}' has all metrics")
        
        print("\n✓ PASSED - Category breakdown works correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_tracking():
    """Test that execution time is tracked"""
    print("\n" + "="*70)
    print("M10 Acceptance Test: Performance Tracking")
    print("="*70 + "\n")
    
    try:
        test_cases = [
            BenchmarkCase(
                question="性能测试",
                expected_sql="SELECT * FROM Track LIMIT 10",
                category="performance"
            )
        ]
        
        runner = BenchmarkRunner()
        report = runner.run_benchmark(test_cases)
        
        # Verify timing data
        summary = report['summary']
        assert 'total_time' in summary, "Missing total_time"
        assert 'avg_time_per_case' in summary, "Missing avg_time_per_case"
        
        assert summary['total_time'] > 0, "Total time should be positive"
        assert summary['avg_time_per_case'] > 0, "Avg time should be positive"
        
        print(f"✓ Total time: {summary['total_time']}s")
        print(f"✓ Avg time per case: {summary['avg_time_per_case']}s")
        
        # Verify individual result has execution_time
        result = report['results'][0]
        assert 'execution_time' in result, "Result missing execution_time"
        assert result['execution_time'] > 0, "Execution time should be positive"
        
        print(f"✓ Individual execution time: {result['execution_time']}s")
        
        print("\n✓ PASSED - Performance tracking works correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Run all M10 acceptance tests"""
    print("\n" + "="*70)
    print("M10 - Benchmark Framework - Full Acceptance Test Suite")
    print("="*70)
    
    tests = [
        ("Benchmark Framework", test_benchmark_framework),
        ("Test Case Loading", test_test_case_loading),
        ("Metrics Calculation", test_metrics_calculation),
        ("Report Generation", test_report_generation),
        ("Category Breakdown", test_category_breakdown),
        ("Performance Tracking", test_performance_tracking)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            failed += 1
    
    # Final summary
    print("\n" + "="*70)
    print(f"Test Summary: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70)
    
    if failed == 0:
        print("🎉 ALL M10 ACCEPTANCE TESTS PASSED!")
    else:
        print("⚠️  SOME M10 TESTS FAILED - Please review above")
    print("="*70)
    
    sys.exit(0 if failed == 0 else 1)
