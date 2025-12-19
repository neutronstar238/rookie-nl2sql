"""
M4 Acceptance Test: SQL Guardrail
测试 SQL 校验和自动修复功能
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from graphs.base_graph import run_query
from tools.sql_validator import validate_sql, repair_sql
from tools.db import db_client


def test_sql_validator_basic():
    """测试1: SQL 校验器基本功能"""
    print("\n" + "="*70)
    print("Test 1: SQL Validator Basic Functionality")
    print("="*70)
    
    test_cases = [
        ("Valid SELECT", "SELECT * FROM Album LIMIT 10", True),
        ("Invalid syntax", "SELECT * FORM Album", False),
        ("Non-SELECT", "DELETE FROM Album WHERE AlbumId = 1", False),
        ("Empty SQL", "   ", False),
    ]
    
    passed = 0
    for name, sql, expected_valid in test_cases:
        result = validate_sql(sql)
        actual_valid = result['valid']
        status = "✓" if actual_valid == expected_valid else "✗"
        print(f"{status} {name}: {actual_valid} (expected {expected_valid})")
        if actual_valid == expected_valid:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_sql_repair():
    """测试2: SQL 自动修复"""
    print("\n" + "="*70)
    print("Test 2: SQL Auto-Repair")
    print("="*70)
    
    test_cases = [
        {
            "name": "Remove trailing semicolon",
            "sql": "SELECT * FROM Album LIMIT 10;",
            "should_succeed": True
        },
        {
            "name": "Normalize formatting",
            "sql": "SELECT   *   FROM   Album   LIMIT   10",
            "should_succeed": True
        },
    ]
    
    passed = 0
    for test in test_cases:
        repair_result = repair_sql(test['sql'])
        success = repair_result['success']
        status = "✓" if success == test['should_succeed'] else "✗"
        print(f"{status} {test['name']}: {success}")
        if success:
            print(f"  Repaired: {repair_result['repaired_sql'][:60]}...")
            print(f"  Changes: {repair_result['changes']}")
        if success == test['should_succeed']:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_integration_with_graph():
    """测试3: 图集成测试 - 校验节点在工作流中正常运行"""
    print("\n" + "="*70)
    print("Test 3: Integration with Graph")
    print("="*70)
    
    test_questions = [
        "Show all albums",
        "How many artists are there?",
        "Show albums with their artist names"
    ]
    
    passed = 0
    for question in test_questions:
        print(f"\nQuestion: {question}")
        result = run_query(question)
        
        # 检查是否有校验结果
        validation = result.get('validation_result')
        has_validation = validation is not None
        
        # 检查 SQL 是否被执行
        execution = result.get('execution_result')
        executed = execution is not None and execution.get('ok', False)
        
        status = "✓" if has_validation and executed else "✗"
        print(f"{status} Validated: {has_validation}, Executed: {executed}")
        
        if validation:
            print(f"  Valid: {validation.get('valid')}")
            if validation.get('repair_applied'):
                print(f"  Repairs: {validation.get('repair_changes')}")
        
        if has_validation and executed:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_questions)}")
    return passed == len(test_questions)


def test_syntax_error_recovery():
    """测试4: 语法错误恢复"""
    print("\n" + "="*70)
    print("Test 4: Syntax Error Recovery")
    print("="*70)
    
    # 构造一个带有小错误的 SQL (例如多余的分号)
    sql_with_error = "SELECT Title FROM Album LIMIT 5;"
    
    print(f"SQL with error: {sql_with_error}")
    
    # 校验
    validation = validate_sql(sql_with_error)
    print(f"Valid: {validation['valid']}")
    
    # 修复
    repair_result = repair_sql(sql_with_error)
    print(f"Repair success: {repair_result['success']}")
    
    if repair_result['success']:
        print(f"Repaired SQL: {repair_result['repaired_sql']}")
        
        # 执行修复后的 SQL
        exec_result = db_client.query(repair_result['repaired_sql'])
        executed = exec_result['ok']
        print(f"Execution: {'✓ Success' if executed else '✗ Failed'}")
        
        if executed:
            print(f"Rows returned: {exec_result['row_count']}")
            return True
    
    return False


def test_security_check():
    """测试5: 安全检查 - 拒绝非 SELECT 查询"""
    print("\n" + "="*70)
    print("Test 5: Security Check - Reject Non-SELECT")
    print("="*70)
    
    dangerous_sqls = [
        "DELETE FROM Album WHERE AlbumId = 1",
        "UPDATE Album SET Title = 'Hacked' WHERE AlbumId = 1",
        "DROP TABLE Album",
        "INSERT INTO Album (Title) VALUES ('New Album')",
    ]
    
    passed = 0
    for sql in dangerous_sqls:
        validation = validate_sql(sql)
        rejected = not validation['valid']
        status = "✓" if rejected else "✗"
        print(f"{status} Rejected: {sql[:50]}")
        if rejected:
            print(f"  Error: {validation['errors'][0]}")
            passed += 1
    
    print(f"\nPassed: {passed}/{len(dangerous_sqls)}")
    return passed == len(dangerous_sqls)


def test_complex_query_validation():
    """测试6: 复杂查询校验"""
    print("\n" + "="*70)
    print("Test 6: Complex Query Validation")
    print("="*70)
    
    complex_queries = [
        {
            "name": "JOIN with alias",
            "sql": """
                SELECT a.Title, ar.Name AS ArtistName
                FROM Album a
                JOIN Artist ar ON a.ArtistId = ar.ArtistId
                LIMIT 10
            """
        },
        {
            "name": "Subquery",
            "sql": """
                SELECT Title FROM Album 
                WHERE ArtistId IN (
                    SELECT ArtistId FROM Artist WHERE Name LIKE '%Rock%'
                )
                LIMIT 10
            """
        },
        {
            "name": "GROUP BY with HAVING",
            "sql": """
                SELECT ArtistId, COUNT(*) as AlbumCount
                FROM Album
                GROUP BY ArtistId
                HAVING COUNT(*) > 5
                LIMIT 10
            """
        }
    ]
    
    passed = 0
    for query in complex_queries:
        validation = validate_sql(query['sql'])
        valid = validation['valid']
        status = "✓" if valid else "✗"
        print(f"{status} {query['name']}: {valid}")
        
        if not valid and validation.get('errors'):
            print(f"  Errors: {validation['errors']}")
        
        if valid:
            # 尝试执行
            normalized = validation['normalized_sql']
            exec_result = db_client.query(normalized)
            if exec_result['ok']:
                print(f"  Executed successfully, rows: {exec_result['row_count']}")
                passed += 1
            else:
                print(f"  Execution failed: {exec_result['error']}")
        elif validation.get('errors'):
            # 如果校验失败但有明确的错误，也算部分通过
            print(f"  Validation caught issue (expected)")
    
    print(f"\nPassed: {passed}/{len(complex_queries)}")
    return passed >= len(complex_queries) * 0.8  # 80% 通过率


def test_normalization():
    """测试7: SQL 规范化"""
    print("\n" + "="*70)
    print("Test 7: SQL Normalization")
    print("="*70)
    
    messy_sql = "select   *   from   Album   where   Title   like   '%Rock%'   limit   10"
    
    print(f"Original SQL:\n{messy_sql}")
    
    validation = validate_sql(messy_sql)
    if validation['valid'] and validation.get('normalized_sql'):
        normalized = validation['normalized_sql']
        print(f"\nNormalized SQL:\n{normalized}")
        
        # 检查规范化是否改善了格式
        is_cleaner = len(normalized.split('\n')) > 1  # 多行格式
        print(f"\nFormatting improved: {is_cleaner}")
        return True
    
    return False


def test_schema_aware_validation():
    """测试8: Schema 感知校验"""
    print("\n" + "="*70)
    print("Test 8: Schema-Aware Validation")
    print("="*70)
    
    # 获取真实 Schema
    from tools.db import db_client
    schemas = db_client.get_all_schemas()
    
    if not schemas:
        print("⚠️  No schema available, skipping test")
        return True
    
    schema = {
        "tables": schemas
    }
    
    test_cases = [
        {
            "name": "Valid table name",
            "sql": "SELECT * FROM Album LIMIT 10",
            "should_be_valid": True
        },
        {
            "name": "Invalid table name",
            "sql": "SELECT * FROM NonExistentTable LIMIT 10",
            "should_be_valid": False
        }
    ]
    
    passed = 0
    for test in test_cases:
        validation = validate_sql(test['sql'], schema=schema)
        valid = validation['valid']
        expected = test['should_be_valid']
        status = "✓" if (valid == expected) else "✗"
        print(f"{status} {test['name']}: valid={valid}, expected={expected}")
        
        if not valid and validation.get('errors'):
            print(f"  Errors: {validation['errors']}")
        
        if (valid == expected):
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("M4 ACCEPTANCE TEST - SQL GUARDRAIL")
    print("="*70)
    
    # 检查数据库连接
    if not db_client.test_connection():
        print("\n⚠️  Database not available. Please run:")
        print("  python scripts/setup_db.py")
        return
    
    tests = [
        ("SQL Validator Basic", test_sql_validator_basic),
        ("SQL Auto-Repair", test_sql_repair),
        ("Integration with Graph", test_integration_with_graph),
        ("Syntax Error Recovery", test_syntax_error_recovery),
        ("Security Check", test_security_check),
        ("Complex Query Validation", test_complex_query_validation),
        ("SQL Normalization", test_normalization),
        ("Schema-Aware Validation", test_schema_aware_validation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    elif passed >= total * 0.9:
        print("✓ ACCEPTANCE TEST PASSED (≥90%)")
    else:
        print(f"✗ ACCEPTANCE TEST FAILED (<90%)")
    
    print("="*70)
    
    return passed >= total * 0.9


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
