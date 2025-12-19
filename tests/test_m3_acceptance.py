"""
M3 Acceptance Test: Schema Ingestion
Validates that database schema is properly loaded and used in SQL generation.

Validation criteria:
- Schema should be loaded from database
- Schema should contain all tables and columns
- Generated SQL should use correct table/column names
- SQL should execute successfully with real schema
- Complex queries (joins, aggregations) should work better
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from graphs.base_graph import run_query
from tools.db import db_client


# Test cases designed to validate schema usage
TEST_CASES = [
    {
        "name": "Schema Loading",
        "question": "Show all albums",
        "expected_keywords": ["Album", "SELECT"],
        "should_succeed": True,
        "check_schema": True,
        "description": "Verify schema is loaded into state"
    },
    {
        "name": "Correct Table Names",
        "question": "List all artists",
        "expected_keywords": ["Artist", "SELECT"],
        "should_succeed": True,
        "description": "Verify LLM uses correct capitalized table names"
    },
    {
        "name": "Correct Column Names",
        "question": "Show track names and their duration in milliseconds",
        "expected_keywords": ["Track", "Name", "Milliseconds"],
        "should_succeed": True,
        "description": "Verify LLM uses exact column names from schema"
    },
    {
        "name": "Foreign Key Relationships",
        "question": "Show albums with their artist names",
        "expected_keywords": ["Album", "Artist", "JOIN", "ArtistId"],
        "should_succeed": True,
        "description": "Verify LLM understands table relationships from schema"
    },
    {
        "name": "Complex Join Query",
        "question": "Show track names with their album titles and artist names",
        "expected_keywords": ["Track", "Album", "Artist", "JOIN"],
        "should_succeed": True,
        "description": "Verify complex multi-table joins work with schema"
    },
    {
        "name": "Aggregation with GroupBy",
        "question": "Count the number of tracks for each genre",
        "expected_keywords": ["Track", "Genre", "COUNT", "GROUP BY"],
        "should_succeed": True,
        "description": "Verify aggregation queries use correct schema"
    },
    {
        "name": "Customer Invoice Query",
        "question": "Show each customer's total spending",
        "expected_keywords": ["Customer", "Invoice", "SUM", "Total"],
        "should_succeed": True,
        "description": "Verify business logic queries with schema"
    },
    {
        "name": "Nested Relationship",
        "question": "Show invoice details with customer and track information",
        "expected_keywords": ["Invoice", "InvoiceLine", "Customer", "Track"],
        "should_succeed": True,
        "description": "Verify deep relationship queries"
    },
    {
        "name": "Date Range Query",
        "question": "Show invoices from 2021",
        "expected_keywords": ["Invoice", "InvoiceDate", "2021"],
        "should_succeed": True,
        "description": "Verify date column usage from schema"
    },
    {
        "name": "Playlist Tracks Query",
        "question": "Show all tracks in the playlist named 'Music'",
        "expected_keywords": ["Playlist", "PlaylistTrack", "Track"],
        "should_succeed": True,
        "description": "Verify many-to-many relationship handling"
    },
    {
        "name": "Employee Hierarchy",
        "question": "Show employees and their managers",
        "expected_keywords": ["Employee", "ReportsTo"],
        "should_succeed": True,
        "description": "Verify self-referencing relationship"
    },
    {
        "name": "Price Calculation",
        "question": "Calculate total sales value for each track",
        "expected_keywords": ["InvoiceLine", "UnitPrice", "Quantity"],
        "should_succeed": True,
        "description": "Verify numeric column operations"
    }
]


def validate_test_case(test_case, result):
    """
    Validate a single test case result.

    Args:
        test_case: Test case dictionary
        result: Execution result state

    Returns:
        tuple: (passed, reason)
    """
    # Check schema loading
    if test_case.get("check_schema"):
        schema = result.get("schema")
        if not schema:
            return False, "Schema not loaded"
        
        if not schema.get("tables"):
            return False, "Schema has no tables"
        
        table_count = schema.get("table_count", 0)
        if table_count < 10:  # Chinook should have 11 tables
            return False, f"Schema incomplete (only {table_count} tables)"
    
    # Check SQL generation
    sql = result.get("candidate_sql")
    if not sql:
        return False, "No SQL generated"

    # Check SQL contains expected keywords (case-sensitive for table/column names)
    for keyword in test_case["expected_keywords"]:
        if keyword not in sql:
            return False, f"Missing keyword: {keyword}"

    # Check execution result
    exec_result = result.get("execution_result")
    if not exec_result:
        return False, "No execution result"

    # Check if execution succeeded
    if test_case["should_succeed"]:
        if not exec_result.get("ok"):
            return False, f"Execution failed: {exec_result.get('error')}"

        # For this test, we allow 0 rows (some queries might return empty results)
        # but we check that the query at least executed without error

    return True, "OK"


def run_acceptance_test():
    """Run M3 acceptance tests."""
    print("=" * 80)
    print("M3 Acceptance Test: Schema Ingestion")
    print("=" * 80)
    print()

    # First, verify database connection and schema availability
    print("Pre-flight checks:")
    print("-" * 80)
    
    if not db_client.test_connection():
        print("✗ Database connection failed!")
        return False
    print("✓ Database connected")
    
    schemas = db_client.get_all_schemas()
    print(f"✓ Found {len(schemas)} tables in database")
    
    if len(schemas) < 10:
        print(f"⚠️  Warning: Expected at least 10 tables, found {len(schemas)}")
    
    print()

    results = []

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}/{len(TEST_CASES)}: {test_case['name']}")
        print(f"{'=' * 80}")
        print(f"Question: {test_case['question']}")
        print(f"Description: {test_case['description']}")

        try:
            # Run query
            result = run_query(test_case['question'])

            # Validate result
            passed, reason = validate_test_case(test_case, result)

            results.append({
                "name": test_case['name'],
                "passed": passed,
                "reason": reason,
                "sql": result.get('candidate_sql'),
                "execution": result.get('execution_result', {}),
                "schema_loaded": result.get('schema') is not None
            })

            if passed:
                print(f"\n✓ Test PASSED")
                print(f"  SQL: {result.get('candidate_sql')}")
                exec_result = result.get('execution_result', {})
                if exec_result.get('ok'):
                    print(f"  Rows: {exec_result.get('row_count', 0)}")
                    print(f"  Columns: {', '.join(exec_result.get('columns', [])[:5])}")
            else:
                print(f"\n✗ Test FAILED: {reason}")
                print(f"  SQL: {result.get('candidate_sql')}")

        except Exception as e:
            print(f"\n✗ Test ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "name": test_case['name'],
                "passed": False,
                "reason": str(e),
                "sql": None,
                "execution": None,
                "schema_loaded": False
            })

    # Summary
    print(f"\n\n{'=' * 80}")
    print("Test Summary")
    print(f"{'=' * 80}")

    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0

    print(f"Passed: {passed_count}/{total_count}")
    print(f"Failed: {total_count - passed_count}/{total_count}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    # Schema loading stats
    schema_loaded_count = sum(1 for r in results if r.get('schema_loaded'))
    print(f"Schema Loaded: {schema_loaded_count}/{total_count} tests")

    # Show failures
    failures = [r for r in results if not r['passed']]
    if failures:
        print(f"\nFailed Tests:")
        for result in failures:
            print(f"  - {result['name']}: {result['reason']}")

    # Acceptance criteria
    print(f"\n{'=' * 80}")
    if pass_rate >= 90:  # Allow 90% pass rate for M3
        print("🎉 ACCEPTANCE TEST PASSED!")
        print(f"{'=' * 80}")
        print("\nM3 module is complete.")
        print("Schema ingestion is working correctly.")
        print("SQL generation now uses real database schema.")
        return True
    else:
        print("❌ ACCEPTANCE TEST FAILED")
        print(f"{'=' * 80}")
        print(f"\nRequired: 90% pass rate")
        print(f"Actual: {pass_rate:.1f}%")
        print("\nPlease fix the failing tests and try again.")
        return False


if __name__ == "__main__":
    success = run_acceptance_test()
    sys.exit(0 if success else 1)
