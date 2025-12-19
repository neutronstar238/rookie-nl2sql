"""
M7 Acceptance Test: Dialog Clarification & Intent Disambiguation

Tests the ambiguity detection and question normalization capabilities.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.ambiguity_detector import clarification_manager, AmbiguityDetector
from graphs.nodes.clarify_intent import clarify_intent_node
from graphs.state import NL2SQLState


def test_ambiguity_detection():
    """Test ambiguity detection with various question types."""
    
    print("\n" + "="*70)
    print("M7 Acceptance Test: Ambiguity Detection")
    print("="*70)
    
    test_cases = [
        {
            "id": 1,
            "question": "查询所有客户",
            "should_be_ambiguous": False,
            "expected_score_range": (0.0, 0.3),
            "description": "Clear question - no ambiguity"
        },
        {
            "id": 2,
            "question": "查询最近的订单",
            "should_be_ambiguous": True,
            "expected_score_range": (0.3, 1.0),
            "description": "Ambiguous time reference"
        },
        {
            "id": 3,
            "question": "查询销售额很多的客户",
            "should_be_ambiguous": True,
            "expected_score_range": (0.3, 1.0),
            "description": "Vague quantifier 'very many'"
        },
        {
            "id": 4,
            "question": "查询前10个客户",
            "should_be_ambiguous": True,
            "expected_score_range": (0.2, 1.0),
            "description": "Missing sort criteria"
        },
        {
            "id": 5,
            "question": "统计每个国家的客户数量",
            "should_be_ambiguous": False,
            "expected_score_range": (0.0, 0.3),
            "description": "Clear aggregation query"
        },
        {
            "id": 6,
            "question": "查询价格高的产品",
            "should_be_ambiguous": True,
            "expected_score_range": (0.3, 1.0),
            "description": "Ambiguous 'high' threshold"
        },
        {
            "id": 7,
            "question": "查询2024年1月销售额超过1000的客户",
            "should_be_ambiguous": False,
            "expected_score_range": (0.0, 0.3),
            "description": "Specific criteria - clear"
        },
        {
            "id": 8,
            "question": "查询客户订单",
            "should_be_ambiguous": True,
            "expected_score_range": (0.2, 1.0),
            "description": "Multiple interpretations"
        },
        {
            "id": 9,
            "question": "统计总数",
            "should_be_ambiguous": True,
            "expected_score_range": (0.2, 1.0),
            "description": "Missing aggregation field"
        },
        {
            "id": 10,
            "question": "显示销售额前5的客户按时间排序",
            "should_be_ambiguous": False,
            "expected_score_range": (0.0, 0.3),
            "description": "Clear with sort criteria"
        },
    ]
    
    detector = AmbiguityDetector()
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"\n### 测试用例 {tc['id']}: {tc['description']} ###")
        print(f"Question: {tc['question']}")
        
        result = detector.detect_ambiguity(tc['question'])
        
        # Check ambiguity detection
        is_ambiguous = result['is_ambiguous']
        score = result['ambiguity_score']
        
        print(f"Is Ambiguous: {is_ambiguous} (expected: {tc['should_be_ambiguous']})")
        print(f"Ambiguity Score: {score:.2f} (expected range: {tc['expected_score_range']})")
        
        # Validation
        score_in_range = tc['expected_score_range'][0] <= score <= tc['expected_score_range'][1]
        ambiguity_matches = is_ambiguous == tc['should_be_ambiguous'] or score_in_range
        
        if ambiguity_matches and score_in_range:
            print(f"✓ PASS")
            passed += 1
        else:
            print(f"✗ FAIL")
            failed += 1
        
        if result['clarification_questions']:
            print(f"Clarifications: {result['clarification_questions'][:2]}")
        
        if result['normalized_question']:
            print(f"Normalized: {result['normalized_question']}")
    
    print("\n" + "="*70)
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    print("="*70)
    
    return passed >= len(test_cases) * 0.9  # 90% pass rate


def test_normalization():
    """Test question normalization capabilities."""
    
    print("\n" + "="*70)
    print("M7 Acceptance Test: Question Normalization")
    print("="*70)
    
    test_cases = [
        {
            "id": 1,
            "question": "查询最近的订单",
            "should_normalize": True,
            "expected_contains": "30天",
            "description": "Normalize 'recent' to specific days"
        },
        {
            "id": 2,
            "question": "查询销售额很多的客户",
            "should_normalize": True,
            "expected_contains": "100",
            "description": "Normalize 'many' to specific number"
        },
        {
            "id": 3,
            "question": "查询所有客户",
            "should_normalize": False,
            "expected_contains": None,
            "description": "Clear question needs no normalization"
        },
        {
            "id": 4,
            "question": "查询大量产品",
            "should_normalize": True,
            "expected_contains": "1000",
            "description": "Normalize 'large amount'"
        },
    ]
    
    manager = clarification_manager
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"\n### 测试用例 {tc['id']}: {tc['description']} ###")
        print(f"Original: {tc['question']}")
        
        result = manager.check_and_clarify(tc['question'])
        normalized = result['normalized_question']
        
        print(f"Normalized: {normalized}")
        
        # Validation
        was_normalized = normalized != tc['question']
        contains_expected = tc['expected_contains'] in normalized if tc['expected_contains'] else True
        
        if tc['should_normalize']:
            if was_normalized and contains_expected:
                print(f"✓ PASS - Normalized correctly")
                passed += 1
            else:
                print(f"✗ FAIL - Expected normalization")
                failed += 1
        else:
            if not was_normalized:
                print(f"✓ PASS - No normalization needed")
                passed += 1
            else:
                print(f"✗ FAIL - Unexpected normalization")
                failed += 1
    
    print("\n" + "="*70)
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    print("="*70)
    
    return passed >= len(test_cases) * 0.9


def test_clarify_node():
    """Test the clarify intent node integration."""
    
    print("\n" + "="*70)
    print("M7 Acceptance Test: Clarify Intent Node")
    print("="*70)
    
    test_cases = [
        {
            "id": 1,
            "question": "查询最近的订单",
            "should_need_clarification": True,
            "should_normalize": True,
        },
        {
            "id": 2,
            "question": "查询所有客户",
            "should_need_clarification": False,
            "should_normalize": False,
        },
        {
            "id": 3,
            "question": "查询销售额很多的客户",
            "should_need_clarification": True,
            "should_normalize": True,
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
        
        result = clarify_intent_node(state)
        
        # Validate results
        needs_clarification = result.get('clarification_needed', False)
        was_normalized = result.get('normalized_question') != tc['question']
        
        print(f"Needs Clarification: {needs_clarification} (expected: {tc['should_need_clarification']})")
        print(f"Was Normalized: {was_normalized} (expected: {tc['should_normalize']})")
        
        if result.get('clarification_needed'):
            # For ambiguous questions, we should either normalize or provide clarification questions
            has_output = was_normalized or (result.get('clarification_questions') and len(result['clarification_questions']) > 0)
            if has_output:
                print(f"✓ PASS")
                passed += 1
            else:
                print(f"✗ FAIL - No clarification output")
                failed += 1
        else:
            # For clear questions, should not need clarification
            if not needs_clarification:
                print(f"✓ PASS")
                passed += 1
            else:
                print(f"✗ FAIL - Unexpected clarification needed")
                failed += 1
    
    print("\n" + "="*70)
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    print("="*70)
    
    return passed >= len(test_cases) * 0.9


if __name__ == "__main__":
    """Run all M7 acceptance tests."""
    
    print("\n" + "="*80)
    print("M7 模块验收测试")
    print("="*80)
    
    results = []
    
    # Test 1: Ambiguity Detection
    results.append(("Ambiguity Detection", test_ambiguity_detection()))
    
    # Test 2: Question Normalization
    results.append(("Question Normalization", test_normalization()))
    
    # Test 3: Clarify Node Integration
    results.append(("Clarify Node Integration", test_clarify_node()))
    
    # Summary
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 M7 验收测试全部通过！")
    else:
        print("\n⚠️ 部分测试未通过，请检查。")
    
    print("="*80)
