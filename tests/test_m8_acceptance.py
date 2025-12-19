"""
M8 Acceptance Test: Multi-table JOIN & Few-shot Templates

Tests the JOIN template matching and complexity analysis capabilities.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.join_template_matcher import join_template_library, JoinTemplateLibrary
from graphs.nodes.match_join_template import match_join_template_node
from graphs.state import NL2SQLState


def test_template_matching():
    """Test template matching for various JOIN patterns."""
    
    print("\n" + "="*70)
    print("M8 Acceptance Test: Template Matching")
    print("="*70)
    
    test_cases = [
        {
            "id": 1,
            "question": "查询每个客户的订单总额",
            "expected_template": "customer_invoice",
            "expected_complexity": "simple",
            "should_match": True,
            "description": "Simple 2-table JOIN"
        },
        {
            "id": 2,
            "question": "查询所有专辑及其艺术家",
            "expected_template": "album_artist",
            "expected_complexity": "simple",
            "should_match": True,
            "description": "Album-Artist relationship"
        },
        {
            "id": 3,
            "question": "查询所有歌曲及其艺术家",
            "expected_template": "track_album_artist",
            "expected_complexity": "medium",
            "should_match": True,
            "description": "3-table chain JOIN"
        },
        {
            "id": 4,
            "question": "统计每个音乐风格的歌曲数量",
            "expected_template": "track_genre_stats",
            "expected_complexity": "simple",
            "should_match": True,
            "description": "Genre statistics"
        },
        {
            "id": 5,
            "question": "查询最畅销的歌曲",
            "expected_template": "invoice_track_sales",
            "expected_complexity": "complex",
            "should_match": True,
            "description": "Sales analysis"
        },
        {
            "id": 6,
            "question": "查询客户购买的所有歌曲",
            "expected_template": "customer_purchase_history",
            "expected_complexity": "complex",
            "should_match": True,
            "description": "4-table JOIN"
        },
        {
            "id": 7,
            "question": "查询播放列表中的所有歌曲",
            "expected_template": "playlist_tracks",
            "expected_complexity": "medium",
            "should_match": True,
            "description": "Many-to-many relationship"
        },
        {
            "id": 8,
            "question": "查询员工及其直接上级",
            "expected_template": "employee_hierarchy",
            "expected_complexity": "medium",
            "should_match": True,
            "description": "Self-join"
        },
        {
            "id": 9,
            "question": "统计每个国家的客户数和销售额",
            "expected_template": "country_sales_stats",
            "expected_complexity": "medium",
            "should_match": True,
            "description": "Country statistics"
        },
        {
            "id": 10,
            "question": "查询每个客户最喜欢的音乐风格",
            "expected_template": "customer_genre_preference",
            "expected_complexity": "complex",
            "should_match": True,
            "description": "5-table complex JOIN"
        },
        {
            "id": 11,
            "question": "查询所有客户的基本信息",
            "expected_template": None,
            "expected_complexity": "simple",
            "should_match": False,
            "description": "No JOIN needed"
        },
        {
            "id": 12,
            "question": "统计总订单数",
            "expected_template": None,
            "expected_complexity": "simple",
            "should_match": False,
            "description": "Single table aggregation"
        },
    ]
    
    library = JoinTemplateLibrary()
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"\n### 测试用例 {tc['id']}: {tc['description']} ###")
        print(f"Question: {tc['question']}")
        
        analysis = library.analyze_join_complexity(tc['question'])
        
        # Check if template matched
        has_match = analysis['has_template']
        complexity = analysis['complexity']
        
        print(f"Has Match: {has_match} (expected: {tc['should_match']})")
        print(f"Complexity: {complexity} (expected: {tc['expected_complexity']})")
        
        # Validation
        match_correct = has_match == tc['should_match']
        complexity_correct = complexity == tc['expected_complexity']
        
        # If should match, check template ID
        if tc['should_match'] and has_match:
            best_match = analysis.get('best_match', {})
            template_id = best_match.get('template_id', '')
            template_correct = template_id == tc['expected_template']
            print(f"Template ID: {template_id} (expected: {tc['expected_template']})")
            
            if match_correct and template_correct:
                print(f"✓ PASS")
                passed += 1
            else:
                print(f"✗ FAIL - Template mismatch")
                failed += 1
        else:
            if match_correct and complexity_correct:
                print(f"✓ PASS")
                passed += 1
            else:
                print(f"✗ FAIL")
                failed += 1
        
        if analysis['suggested_templates']:
            print(f"Suggested Templates:")
            for template in analysis['suggested_templates'][:2]:
                print(f"  - {template['name']} (score: {template['score']:.2f})")
    
    print("\n" + "="*70)
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    print("="*70)
    
    return passed >= len(test_cases) * 0.9  # 90% pass rate


def test_complexity_analysis():
    """Test JOIN complexity classification."""
    
    print("\n" + "="*70)
    print("M8 Acceptance Test: Complexity Analysis")
    print("="*70)
    
    test_cases = [
        {
            "id": 1,
            "question": "查询所有客户",
            "expected_complexity": "simple",
            "expected_table_count": 1,
        },
        {
            "id": 2,
            "question": "查询客户的订单",
            "expected_complexity": "simple",
            "expected_table_count": 2,
        },
        {
            "id": 3,
            "question": "查询歌曲及其艺术家",
            "expected_complexity": "medium",
            "expected_table_count": 3,
        },
        {
            "id": 4,
            "question": "查询客户购买的歌曲",
            "expected_complexity": "complex",
            "expected_table_count": 4,
        },
        {
            "id": 5,
            "question": "查询客户最喜欢的音乐风格",
            "expected_complexity": "complex",
            "expected_table_count": 5,
        },
    ]
    
    library = join_template_library
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"\n### 测试用例 {tc['id']} ###")
        print(f"Question: {tc['question']}")
        
        analysis = library.analyze_join_complexity(tc['question'])
        
        complexity = analysis['complexity']
        table_count = analysis['table_count']
        
        print(f"Complexity: {complexity} (expected: {tc['expected_complexity']})")
        print(f"Table Count: {table_count} (expected: ~{tc['expected_table_count']})")
        
        # Validation - allow some tolerance in table count
        complexity_correct = complexity == tc['expected_complexity']
        table_count_close = abs(table_count - tc['expected_table_count']) <= 1
        
        if complexity_correct and table_count_close:
            print(f"✓ PASS")
            passed += 1
        else:
            print(f"✗ FAIL")
            failed += 1
    
    print("\n" + "="*70)
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    print("="*70)
    
    return passed >= len(test_cases) * 0.8  # 80% pass rate


def test_template_examples():
    """Test that templates provide valid SQL examples."""
    
    print("\n" + "="*70)
    print("M8 Acceptance Test: Template SQL Examples")
    print("="*70)
    
    library = JoinTemplateLibrary()
    passed = 0
    failed = 0
    
    for i, template in enumerate(library.templates, 1):
        print(f"\n### Template {i}: {template.name} ###")
        print(f"ID: {template.template_id}")
        print(f"Complexity: {template.complexity}")
        print(f"Tables: {', '.join(template.tables)}")
        
        # Check that example SQL is not empty
        has_example = bool(template.example_sql and len(template.example_sql) > 20)
        has_question = bool(template.example_question and len(template.example_question) > 5)
        has_tables = len(template.tables) > 0
        
        # Check that SQL contains JOIN keyword (except for single-table queries)
        has_join = "JOIN" in template.example_sql.upper() or len(template.tables) == 1
        
        if has_example and has_question and has_tables and has_join:
            print(f"✓ PASS - Valid template")
            passed += 1
        else:
            print(f"✗ FAIL - Invalid template")
            failed += 1
            if not has_example:
                print(f"  Missing example SQL")
            if not has_question:
                print(f"  Missing example question")
            if not has_tables:
                print(f"  No tables defined")
            if not has_join:
                print(f"  Multi-table query missing JOIN")
    
    total = len(library.templates)
    print("\n" + "="*70)
    print(f"通过: {passed}/{total}")
    print(f"失败: {failed}/{total}")
    print(f"通过率: {passed/total*100:.1f}%")
    print("="*70)
    
    return passed == total  # All templates must be valid


def test_node_integration():
    """Test the match join template node integration."""
    
    print("\n" + "="*70)
    print("M8 Acceptance Test: Node Integration")
    print("="*70)
    
    test_cases = [
        {
            "id": 1,
            "question": "查询每个客户的订单总额",
            "should_have_templates": True,
        },
        {
            "id": 2,
            "question": "查询所有客户",
            "should_have_templates": False,
        },
        {
            "id": 3,
            "question": "查询客户购买的所有歌曲",
            "should_have_templates": True,
        },
    ]
    
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"\n### 测试用例 {tc['id']} ###")
        print(f"Question: {tc['question']}")
        
        state: NL2SQLState = {
            "question": tc['question'],
            "session_id": f"test_{tc['id']}",
            "timestamp": None,
            "intent": None,
            "candidate_sql": None,
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
            "rag_retrieved_at": None,
            "clarification_needed": None,
            "clarification_questions": None,
            "ambiguity_score": None,
            "normalized_question": None,
            "clarified_at": None,
            "join_complexity": None,
            "suggested_templates": None,
            "template_matched_at": None,
        }
        
        result = match_join_template_node(state)
        
        # Validate results
        has_templates = result.get('suggested_templates') and len(result['suggested_templates']) > 0
        has_complexity = result.get('join_complexity') is not None
        
        print(f"Has Templates: {has_templates} (expected: {tc['should_have_templates']})")
        print(f"Complexity: {result.get('join_complexity')}")
        
        # Node should always set complexity
        if has_complexity:
            if tc['should_have_templates']:
                if has_templates:
                    print(f"✓ PASS")
                    passed += 1
                else:
                    print(f"✗ FAIL - Expected templates")
                    failed += 1
            else:
                # Clear questions may or may not have templates
                print(f"✓ PASS")
                passed += 1
        else:
            print(f"✗ FAIL - No complexity analysis")
            failed += 1
    
    print("\n" + "="*70)
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    print("="*70)
    
    return passed >= len(test_cases) * 0.9


if __name__ == "__main__":
    """Run all M8 acceptance tests."""
    
    print("\n" + "="*80)
    print("M8 模块验收测试")
    print("="*80)
    
    results = []
    
    # Test 1: Template Matching
    results.append(("Template Matching", test_template_matching()))
    
    # Test 2: Complexity Analysis
    results.append(("Complexity Analysis", test_complexity_analysis()))
    
    # Test 3: Template Examples
    results.append(("Template SQL Examples", test_template_examples()))
    
    # Test 4: Node Integration
    results.append(("Node Integration", test_node_integration()))
    
    # Summary
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 M8 验收测试全部通过！")
    else:
        print("\n⚠️ 部分测试未通过，请检查。")
    
    print("="*80)
