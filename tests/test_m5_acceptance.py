"""
M5 Acceptance Test Script
验收标准: 所有安全检查必须通过，危险SQL被拦截，安全SQL被正确修改
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sql_sandbox import sql_sandbox


def test_m5_acceptance():
    """
    M5 验收测试 - SQL执行安全与沙箱
    """
    print("="*70)
    print("M5 验收测试 - 执行安全与沙箱")
    print("="*70)
    
    test_cases = [
        {
            "id": 1,
            "name": "安全查询 - 简单SELECT",
            "sql": "SELECT * FROM Customer;",
            "should_allow": True,
            "should_modify": True,  # Should add LIMIT
            "expected_modifications": ["limit_added"]
        },
        {
            "id": 2,
            "name": "安全查询 - 带合理LIMIT",
            "sql": "SELECT * FROM Customer LIMIT 10;",
            "should_allow": True,
            "should_modify": False
        },
        {
            "id": 3,
            "name": "需要修改 - LIMIT超出限制",
            "sql": "SELECT * FROM Customer LIMIT 5000;",
            "should_allow": True,
            "should_modify": True,
            "expected_modifications": ["limit_reduced"]
        },
        {
            "id": 4,
            "name": "危险操作 - DROP TABLE",
            "sql": "DROP TABLE Customer;",
            "should_allow": False,
            "risk_level": "critical"
        },
        {
            "id": 5,
            "name": "危险操作 - DELETE",
            "sql": "DELETE FROM Customer WHERE CustomerId = 1;",
            "should_allow": False,
            "risk_level": "critical"
        },
        {
            "id": 6,
            "name": "危险操作 - UPDATE",
            "sql": "UPDATE Customer SET Email = 'test@test.com' WHERE CustomerId = 1;",
            "should_allow": False,
            "risk_level": "critical"
        },
        {
            "id": 7,
            "name": "SQL注入尝试 - 多语句",
            "sql": "SELECT * FROM Customer; DROP TABLE Album;",
            "should_allow": False,
            "risk_level": "critical"
        },
        {
            "id": 8,
            "name": "复杂查询 - 多表JOIN",
            "sql": """
                SELECT c.FirstName, c.LastName, SUM(i.Total) as Total
                FROM Customer c
                JOIN Invoice i ON c.CustomerId = i.CustomerId
                GROUP BY c.CustomerId
                ORDER BY Total DESC
            """,
            "should_allow": True,
            "should_modify": True
        },
        {
            "id": 9,
            "name": "复杂查询 - 嵌套子查询",
            "sql": """
                SELECT * FROM Track
                WHERE AlbumId IN (
                    SELECT AlbumId FROM Album
                    WHERE ArtistId IN (
                        SELECT ArtistId FROM Artist WHERE Name LIKE '%AC/DC%'
                    )
                )
            """,
            "should_allow": True,
            "should_modify": True
        },
        {
            "id": 10,
            "name": "安全查询 - WHERE条件",
            "sql": "SELECT * FROM Invoice WHERE Total > 10 LIMIT 50;",
            "should_allow": True,
            "should_modify": False
        },
        {
            "id": 11,
            "name": "安全查询 - GROUP BY聚合",
            "sql": """
                SELECT Country, COUNT(*) as CustomerCount
                FROM Customer
                GROUP BY Country
                ORDER BY CustomerCount DESC
                LIMIT 20;
            """,
            "should_allow": True,
            "should_modify": False
        },
        {
            "id": 12,
            "name": "危险操作 - CREATE TABLE",
            "sql": "CREATE TABLE Test (id INTEGER PRIMARY KEY);",
            "should_allow": False,
            "risk_level": "critical"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n{'='*70}")
        print(f"测试用例 {test_case['id']}: {test_case['name']}")
        print(f"{'='*70}")
        print(f"SQL: {test_case['sql'].strip()[:100]}...")
        
        try:
            result = sql_sandbox.check_sql(test_case['sql'])
            
            checks = {}
            
            # Check 1: Allowed status
            if "should_allow" in test_case:
                checks["允许状态正确"] = result['allowed'] == test_case['should_allow']
            
            # Check 2: Modification status
            if "should_modify" in test_case:
                is_modified = bool(result['modifications'])
                checks["修改状态正确"] = is_modified == test_case['should_modify']
            
            # Check 3: Expected modifications
            if "expected_modifications" in test_case:
                for mod in test_case['expected_modifications']:
                    checks[f"包含修改: {mod}"] = mod in result['modifications']
            
            # Check 4: Risk level
            if "risk_level" in test_case:
                checks["风险等级正确"] = result['risk_level'] == test_case['risk_level']
            
            # Check 5: Safe SQL exists if modified
            if result['modifications']:
                checks["生成安全SQL"] = result['safe_sql'] is not None
            
            all_passed = all(checks.values())
            
            print(f"\n验收检查:")
            for check_name, check_result in checks.items():
                status = "✓" if check_result else "✗"
                print(f"  {status} {check_name}")
            
            print(f"\n结果详情:")
            print(f"  Allowed: {'✓' if result['allowed'] else '✗'}")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Estimated Time: {result['estimated_timeout']:.2f}s")
            
            if result['issues']:
                print(f"\n  Issues ({len(result['issues'])}):")
                for issue in result['issues']:
                    print(f"    - {issue}")
            
            if result['warnings']:
                print(f"\n  Warnings ({len(result['warnings'])}):")
                for warning in result['warnings']:
                    print(f"    - {warning}")
            
            if result['modifications']:
                print(f"\n  Modifications: {list(result['modifications'].keys())}")
            
            if all_passed:
                print(f"\n✓ 测试用例 {test_case['id']} 通过")
                passed += 1
            else:
                print(f"\n✗ 测试用例 {test_case['id']} 失败")
                failed += 1
                
        except Exception as e:
            print(f"\n✗ 测试用例 {test_case['id']} 出错: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # 输出总结
    print(f"\n{'='*70}")
    print("测试总结")
    print(f"{'='*70}")
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    
    # 验收标准: 100% (所有安全检查必须正确)
    success_rate = passed / len(test_cases) * 100
    
    if success_rate == 100:
        print("\n🎉 恭喜! M5 验收测试通过!")
        print("✓ SQL安全检查功能正常")
        print("✓ 危险操作成功拦截")
        print("✓ 安全修改正确应用")
        print("✓ 满足验收标准 (100%)")
        print("\n下一步: 开始 M6 模块开发 (RAG行业黑话与QA-SQL检索)")
        return True
    else:
        print(f"\n⚠️  未达到验收标准 (当前: {success_rate:.1f}%, 要求: 100%)")
        print("\n可能的原因:")
        print("1. 安全检查逻辑需要优化")
        print("2. 修改策略不正确")
        print("3. 风险等级判断有误")
        return False


if __name__ == "__main__":
    success = test_m5_acceptance()
    sys.exit(0 if success else 1)
