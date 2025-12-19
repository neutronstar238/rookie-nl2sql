"""
SQL Validation Node (M4)
校验和修复生成的 SQL 语句
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from graphs.state import NL2SQLState
from tools.sql_validator import validate_sql, repair_sql
from datetime import datetime
import json


def validate_sql_node(state: NL2SQLState) -> NL2SQLState:
    """
    校验 SQL 节点：校验生成的 SQL 并尝试自动修复
    
    工作流程:
    1. 从 State 获取 candidate_sql
    2. 使用 Schema 进行校验
    3. 如果校验失败，尝试自动修复
    4. 将校验/修复结果存入 State
    """
    print(f"\n=== Validate SQL Node ===")
    
    # 1. 获取生成的 SQL
    candidate_sql = state.get("candidate_sql")
    if not candidate_sql:
        print("⚠️  No SQL to validate")
        return {
            **state,
            "validation_result": {
                "valid": False,
                "error": "No SQL to validate",
                "validated_at": datetime.now().isoformat()
            },
            "validated_at": datetime.now().isoformat()
        }
    
    print(f"Original SQL:\n{candidate_sql}")
    
    # 2. 获取 Schema (用于语义校验)
    schema = state.get("schema")
    
    # 3. 校验 SQL
    validation_result = validate_sql(
        candidate_sql, 
        schema=schema,
        strict_mode=False  # 可以设置为 True 启用严格模式
    )
    
    print(f"Validation: {'✓ Valid' if validation_result['valid'] else '✗ Invalid'}")
    
    if validation_result['errors']:
        print(f"Errors:")
        for error in validation_result['errors']:
            print(f"  - {error}")
    
    if validation_result['warnings']:
        print(f"Warnings:")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")
    
    # 4. 如果校验失败，尝试修复
    repaired_sql = candidate_sql
    repair_applied = False
    repair_changes = []
    
    if not validation_result['valid']:
        print("\n--- Attempting Auto-Repair ---")
        repair_result = repair_sql(candidate_sql, schema=schema)
        
        if repair_result['success']:
            repaired_sql = repair_result['repaired_sql']
            repair_changes = repair_result['changes']
            repair_applied = True
            
            print(f"✓ Repair successful")
            print(f"Changes:")
            for change in repair_changes:
                print(f"  - {change}")
            print(f"\nRepaired SQL:\n{repaired_sql}")
            
            # 更新校验结果
            validation_result = repair_result['validation']
        else:
            print(f"✗ Repair failed")
            if repair_result.get('validation', {}).get('errors'):
                print(f"Remaining errors:")
                for error in repair_result['validation']['errors']:
                    print(f"  - {error}")
    else:
        # 即使校验通过，也应用规范化
        if validation_result.get('normalized_sql'):
            repaired_sql = validation_result['normalized_sql']
            repair_changes.append("Applied SQL normalization")
            print(f"\nNormalized SQL:\n{repaired_sql}")
    
    # 5. 构建校验结果
    final_validation = {
        "valid": validation_result['valid'],
        "errors": validation_result.get('errors', []),
        "warnings": validation_result.get('warnings', []),
        "repair_applied": repair_applied,
        "repair_changes": repair_changes,
        "original_sql": candidate_sql,
        "validated_sql": repaired_sql,
        "validated_at": datetime.now().isoformat()
    }
    
    # 6. 更新 State
    return {
        **state,
        "candidate_sql": repaired_sql,  # 使用修复后的 SQL
        "validation_result": final_validation,
        "validated_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    """测试 SQL 校验节点"""
    print("="*60)
    print("Validate SQL Node Test")
    print("="*60)
    
    # 测试用例
    test_cases = [
        {
            "name": "Valid SQL",
            "candidate_sql": "SELECT * FROM Album LIMIT 10"
        },
        {
            "name": "SQL with syntax error",
            "candidate_sql": "SELECT * FORM Album"  # FORM -> FROM
        },
        {
            "name": "SQL with extra semicolon",
            "candidate_sql": "SELECT * FROM Album LIMIT 10;"
        },
        {
            "name": "Complex JOIN",
            "candidate_sql": """
                SELECT a.Title, ar.Name 
                FROM Album a 
                JOIN Artist ar ON a.ArtistId = ar.ArtistId
            """
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {test['name']}")
        print(f"{'='*60}")
        
        # 构建测试 State
        state: NL2SQLState = {
            "question": "Test question",
            "timestamp": datetime.now().isoformat(),
            "session_id": f"test-{i}",
            "intent": None,
            "candidate_sql": test['candidate_sql'],
            "sql_generated_at": datetime.now().isoformat(),
            "execution_result": None,
            "executed_at": None,
            "schema": None,
            "schema_loaded_at": None
        }
        
        # 执行校验节点
        result = validate_sql_node(state)
        
        # 显示结果
        validation = result.get('validation_result', {})
        print(f"\nResult: {'✓ Valid' if validation.get('valid') else '✗ Invalid'}")
        print(f"Final SQL: {result.get('candidate_sql')}")
        
        if validation.get('repair_applied'):
            print(f"Repairs Applied: {validation.get('repair_changes')}")
    
    print("\n" + "="*60)
    print("Validate SQL Node Test Complete!")
    print("="*60)
