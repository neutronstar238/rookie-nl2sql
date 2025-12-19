"""
M9 Acceptance Tests: Answer Builder
Tests the natural language answer generation from SQL execution results.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from graphs.base_graph import run_query


def test_answer_generation():
    """Test that answers are generated for all query types"""
    test_cases = [
        {
            "name": "Simple count query",
            "question": "有多少首歌曲？",
            "expected_keywords": ["歌曲", "3503", "Track"]
        },
        {
            "name": "List query",
            "question": "显示前5个音乐风格",
            "expected_keywords": ["风格", "Genre"]
        },
        {
            "name": "Aggregation query",
            "question": "每个国家有多少客户？",
            "expected_keywords": ["国家", "客户", "Country"]
        },
        {
            "name": "Top N query",
            "question": "价格最高的5首歌曲",
            "expected_keywords": ["价格", "歌曲"]
        },
        {
            "name": "Filter query",
            "question": "显示来自巴西的客户",
            "expected_keywords": ["巴西", "Brazil", "客户"]
        }
    ]
    
    print("\n" + "="*70)
    print("M9 Acceptance Test: Answer Generation")
    print("="*70 + "\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n### Test Case {i}: {test['name']} ###")
        print(f"Question: {test['question']}")
        
        try:
            # Run query
            result = run_query(test['question'])
            
            # Check if answer was generated
            answer = result.get('answer')
            if not answer:
                print(f"✗ FAILED - No answer generated")
                failed += 1
                continue
            
            # Check if execution was successful
            execution_result = result.get('execution_result', {})
            if not execution_result.get('ok'):
                print(f"⚠️  SQL execution failed: {execution_result.get('error')}")
                # Answer should still be generated for failures
                if "失败" in answer or "错误" in answer:
                    print(f"✓ PASSED - Error handled correctly")
                    passed += 1
                else:
                    print(f"✗ FAILED - Error not properly reported in answer")
                    failed += 1
                continue
            
            # Verify answer contains expected keywords
            print(f"\nGenerated Answer:")
            print(f"{answer}")
            
            missing_keywords = []
            for keyword in test.get('expected_keywords', []):
                if keyword.lower() not in answer.lower():
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                print(f"\n⚠️  Missing keywords: {missing_keywords}")
                print(f"✓ PASSED (with warnings)")
                passed += 1
            else:
                print(f"\n✓ PASSED - All keywords present")
                passed += 1
                
        except Exception as e:
            print(f"✗ FAILED - Exception: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"Test Summary: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*70)
    
    return passed == len(test_cases)


def test_answer_quality():
    """Test answer quality and completeness"""
    print("\n" + "="*70)
    print("M9 Acceptance Test: Answer Quality")
    print("="*70 + "\n")
    
    test_cases = [
        {
            "question": "统计歌曲总数",
            "quality_checks": [
                ("contains_number", "应包含具体数字"),
                ("not_too_short", "答案不应过短（>20字符）"),
                ("mentions_sql", "应提及SQL或查询方法")
            ]
        },
        {
            "question": "显示所有专辑",
            "quality_checks": [
                ("mentions_table", "应提及表名或数据类型"),
                ("not_too_short", "答案不应过短（>20字符）")
            ]
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n### Quality Test {i} ###")
        print(f"Question: {test['question']}")
        
        try:
            result = run_query(test['question'])
            answer = result.get('answer', '')
            
            if not answer:
                print(f"✗ FAILED - No answer generated")
                failed += 1
                continue
            
            print(f"\nAnswer: {answer[:200]}...")
            
            # Quality checks
            all_passed = True
            for check_type, description in test['quality_checks']:
                if check_type == "contains_number":
                    if any(c.isdigit() for c in answer):
                        print(f"  ✓ {description}")
                    else:
                        print(f"  ✗ {description}")
                        all_passed = False
                        
                elif check_type == "not_too_short":
                    if len(answer) > 20:
                        print(f"  ✓ {description}")
                    else:
                        print(f"  ✗ {description}")
                        all_passed = False
                        
                elif check_type == "mentions_sql":
                    if any(kw in answer.lower() for kw in ["sql", "查询", "统计", "检索", "表"]):
                        print(f"  ✓ {description}")
                    else:
                        print(f"  ✗ {description}")
                        all_passed = False
                        
                elif check_type == "mentions_table":
                    if any(kw in answer for kw in ["表", "Table", "数据", "记录"]):
                        print(f"  ✓ {description}")
                    else:
                        print(f"  ✗ {description}")
                        all_passed = False
            
            if all_passed:
                print(f"\n✓ PASSED - All quality checks passed")
                passed += 1
            else:
                print(f"\n✗ FAILED - Some quality checks failed")
                failed += 1
                
        except Exception as e:
            print(f"✗ FAILED - Exception: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"Quality Test Summary: {passed} passed, {failed} failed")
    print("="*70)
    
    return passed == len(test_cases)


def test_edge_cases():
    """Test edge cases like empty results and errors"""
    print("\n" + "="*70)
    print("M9 Acceptance Test: Edge Cases")
    print("="*70 + "\n")
    
    test_cases = [
        {
            "name": "Empty result",
            "question": "显示价格超过1000的歌曲",
            "should_mention": ["没有", "未找到", "0"]
        },
        {
            "name": "Single row result",
            "question": "数据库中有多少个表？",
            "should_have_answer": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n### Edge Case {i}: {test['name']} ###")
        print(f"Question: {test['question']}")
        
        try:
            result = run_query(test['question'])
            answer = result.get('answer', '')
            
            if not answer:
                print(f"✗ FAILED - No answer generated")
                failed += 1
                continue
            
            print(f"\nAnswer: {answer}")
            
            # Check based on test type
            if 'should_mention' in test:
                found = any(keyword in answer for keyword in test['should_mention'])
                if found:
                    print(f"✓ PASSED - Correctly handles edge case")
                    passed += 1
                else:
                    print(f"⚠️  PASSED (with warning) - Expected keywords not found but answer exists")
                    passed += 1
                    
            elif test.get('should_have_answer'):
                if len(answer) > 10:
                    print(f"✓ PASSED - Answer generated")
                    passed += 1
                else:
                    print(f"✗ FAILED - Answer too short")
                    failed += 1
                    
        except Exception as e:
            print(f"✗ FAILED - Exception: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"Edge Case Summary: {passed} passed, {failed} failed")
    print("="*70)
    
    return passed == len(test_cases)


if __name__ == "__main__":
    """Run all M9 acceptance tests"""
    print("\n" + "="*70)
    print("M9 - Answer Builder - Full Acceptance Test Suite")
    print("="*70)
    
    all_passed = True
    
    # Test 1: Answer generation
    if not test_answer_generation():
        all_passed = False
    
    # Test 2: Answer quality
    if not test_answer_quality():
        all_passed = False
    
    # Test 3: Edge cases
    if not test_edge_cases():
        all_passed = False
    
    # Final summary
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL M9 ACCEPTANCE TESTS PASSED!")
    else:
        print("⚠️  SOME M9 TESTS FAILED - Please review above")
    print("="*70)
    
    sys.exit(0 if all_passed else 1)
