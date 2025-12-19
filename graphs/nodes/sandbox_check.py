"""
Sandbox Check Node for NL2SQL system.
M5: Checks SQL safety before execution and applies modifications if needed.
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from graphs.state import NL2SQLState
from tools.sql_sandbox import sql_sandbox


def sandbox_check_node(state: NL2SQLState) -> NL2SQLState:
    """
    Check SQL query safety using sandbox before execution.
    
    Features:
    - Detects dangerous operations
    - Enforces row limits
    - Estimates execution time
    - Applies safe modifications
    
    Args:
        state: Current NL2SQL state with candidate_sql
        
    Returns:
        Updated state with sandbox_check result
    """
    print(f"\n=== Sandbox Check Node ===")
    
    # Get SQL from validation result (if repaired) or original candidate_sql
    validation_result = state.get("validation_result")
    if validation_result and validation_result.get("repaired_sql"):
        sql = validation_result["repaired_sql"]
        print(f"Using repaired SQL from validation")
    else:
        sql = state.get("candidate_sql", "")
        print(f"Using original candidate SQL")
    
    if not sql:
        print(f"✗ No SQL to check")
        return {
            **state,
            "sandbox_check": {
                "allowed": False,
                "risk_level": "critical",
                "issues": ["No SQL provided"],
                "warnings": [],
                "modifications": {},
                "safe_sql": None
            },
            "sandbox_checked_at": datetime.now().isoformat()
        }
    
    print(f"Original SQL:\n{sql}")
    
    # Run sandbox check
    check_result = sql_sandbox.check_sql(sql)
    
    print(f"\nSandbox Check Result:")
    print(f"  Allowed: {'✓' if check_result['allowed'] else '✗'}")
    print(f"  Risk Level: {check_result['risk_level']}")
    print(f"  Estimated Time: {check_result['estimated_timeout']:.2f}s")
    
    if check_result['issues']:
        print(f"\n  Issues:")
        for issue in check_result['issues']:
            print(f"    ✗ {issue}")
    
    if check_result['warnings']:
        print(f"\n  Warnings:")
        for warning in check_result['warnings']:
            print(f"    ⚠️  {warning}")
    
    if check_result['modifications']:
        print(f"\n  Modifications Applied:")
        for key, value in check_result['modifications'].items():
            print(f"    - {key}: {value}")
    
    # Use safe SQL if modifications were applied
    final_sql = check_result['safe_sql']
    
    if final_sql != sql:
        print(f"\nSafe SQL:\n{final_sql}")
        # Update candidate_sql with safe version
        state = {**state, "candidate_sql": final_sql}
    
    return {
        **state,
        "sandbox_check": check_result,
        "sandbox_checked_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    """Test sandbox check node"""
    print("=== Sandbox Check Node Test ===\n")
    
    test_cases = [
        {
            "name": "Safe query without LIMIT",
            "sql": "SELECT * FROM Customer;",
            "expected_modified": True
        },
        {
            "name": "Safe query with LIMIT",
            "sql": "SELECT * FROM Customer LIMIT 10;",
            "expected_modified": False
        },
        {
            "name": "Dangerous query",
            "sql": "DROP TABLE Customer;",
            "expected_allowed": False
        },
        {
            "name": "Complex query",
            "sql": """
                SELECT c.FirstName, SUM(i.Total) as Total
                FROM Customer c
                JOIN Invoice i ON c.CustomerId = i.CustomerId
                GROUP BY c.CustomerId
                ORDER BY Total DESC
            """,
            "expected_modified": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        test_state: NL2SQLState = {
            "question": "Test question",
            "session_id": f"test-{i}",
            "timestamp": None,
            "intent": None,
            "candidate_sql": test_case['sql'],
            "sql_generated_at": None,
            "execution_result": None,
            "executed_at": None,
            "schema": None,
            "schema_loaded_at": None,
            "validation_result": None,
            "validated_at": None,
            "sandbox_check": None,
            "sandbox_checked_at": None,
            "rag_evidence": None,
            "rag_retrieved_at": None
        }
        
        result = sandbox_check_node(test_state)
        
        sandbox_check = result.get('sandbox_check', {})
        print(f"\n✓ Sandbox check completed")
        print(f"  Allowed: {sandbox_check.get('allowed')}")
        print(f"  Risk Level: {sandbox_check.get('risk_level')}")
        print(f"  Modified: {bool(sandbox_check.get('modifications'))}")
    
    print(f"\n{'='*60}")
    print("Test Complete!")
    print(f"{'='*60}")
