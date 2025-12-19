"""
M6 Acceptance Test Script
验收标准: RAG检索功能正常，能够识别行业术语并检索相似QA-SQL对
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.rag_retriever import rag_retriever


def test_m6_acceptance():
    """
    M6 验收测试 - RAG行业黑话与QA-SQL检索
    """
    print("="*70)
    print("M6 验收测试 - RAG行业黑话与QA-SQL检索")
    print("="*70)
    
    test_cases = [
        {
            "id": 1,
            "name": "基础表名映射 - 客户",
            "question": "查询所有客户",
            "expected_terms": ["客户"],
            "should_have_evidence": True
        },
        {
            "id": 2,
            "name": "基础表名映射 - 订单",
            "question": "统计总订单数",
            "expected_terms": ["订单"],
            "should_have_evidence": True
        },
        {
            "id": 3,
            "name": "基础表名映射 - 产品/歌曲",
            "question": "查询所有产品的价格",
            "expected_terms": ["产品", "价格"],
            "should_have_evidence": True
        },
        {
            "id": 4,
            "name": "列名映射 - 城市/国家",
            "question": "统计每个城市和国家的客户数量",
            "expected_terms": ["城市", "国家", "客户"],
            "should_have_evidence": True
        },
        {
            "id": 5,
            "name": "聚合函数映射 - 销售额",
            "question": "查询销售额最高的客户",
            "expected_terms": ["销售额", "客户"],
            "should_have_evidence": True
        },
        {
            "id": 6,
            "name": "聚合函数映射 - 平均价格",
            "question": "统计每个分类的平均价格",
            "expected_terms": ["分类", "平均价格"],
            "should_have_evidence": True
        },
        {
            "id": 7,
            "name": "复合术语识别",
            "question": "查询每个国家的客户总销售额和平均价格",
            "expected_terms": ["国家", "客户"],
            "should_have_evidence": True
        },
        {
            "id": 8,
            "name": "相似查询检索 - 统计客户",
            "question": "统计每个国家有多少客户",
            "should_have_similar": True,
            "min_similarity": 0.1
        },
        {
            "id": 9,
            "name": "相似查询检索 - 价格范围",
            "question": "查询价格在1元到2元之间的歌曲",
            "should_have_similar": True,
            "min_similarity": 0.1
        },
        {
            "id": 10,
            "name": "相似查询检索 - TOP查询",
            "question": "查询销售额排名前5的客户",
            "should_have_similar": True,
            "min_similarity": 0.1
        },
        {
            "id": 11,
            "name": "多术语识别",
            "question": "查询每个艺术家的专辑数量和总销售额",
            "expected_terms": ["艺术家", "专辑", "销售额"],
            "should_have_evidence": True
        },
        {
            "id": 12,
            "name": "无匹配术语",
            "question": "SELECT * FROM Unknown",
            "should_have_evidence": False  # 没有术语匹配，但可能有相似查询
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n{'='*70}")
        print(f"测试用例 {test_case['id']}: {test_case['name']}")
        print(f"{'='*70}")
        print(f"Question: {test_case['question']}")
        
        try:
            result = rag_retriever.retrieve(test_case['question'], top_k=3)
            
            checks = {}
            
            # Check 1: Evidence existence
            if "should_have_evidence" in test_case:
                has_evidence = result['has_evidence']
                checks["证据存在性"] = has_evidence == test_case['should_have_evidence']
            
            # Check 2: Expected terms recognized
            if "expected_terms" in test_case:
                recognized_term_texts = [t['term'] for t in result['recognized_terms']]
                for term in test_case['expected_terms']:
                    checks[f"识别术语: {term}"] = term in recognized_term_texts
            
            # Check 3: Similar examples retrieved
            if "should_have_similar" in test_case:
                has_similar = len(result['similar_examples']) > 0
                checks["检索到相似查询"] = has_similar == test_case['should_have_similar']
            
            # Check 4: Minimum similarity threshold
            if "min_similarity" in test_case and result['similar_examples']:
                top_similarity = result['similar_examples'][0]['similarity']
                checks["相似度达标"] = top_similarity >= test_case['min_similarity']
            
            all_passed = all(checks.values())
            
            print(f"\n验收检查:")
            for check_name, check_result in checks.items():
                status = "✓" if check_result else "✗"
                print(f"  {status} {check_name}")
            
            print(f"\n结果详情:")
            print(f"  Has Evidence: {'✓' if result['has_evidence'] else '✗'}")
            print(f"  Recognized Terms: {len(result['recognized_terms'])}")
            
            if result['recognized_terms']:
                print(f"\n  术语列表:")
                for term in result['recognized_terms']:
                    print(f"    - '{term['term']}' → {term['target']} ({term['type']})")
            
            if result['similar_examples']:
                print(f"\n  相似查询 (Top {len(result['similar_examples'])}):")
                for i, ex in enumerate(result['similar_examples'][:3], 1):
                    print(f"    {i}. {ex['question']} (相似度: {ex['similarity']:.2f})")
            
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
    
    # 验收标准: ≥90% (允许少量边界情况失败)
    success_rate = passed / len(test_cases) * 100
    
    if success_rate >= 90:
        print("\n🎉 恭喜! M6 验收测试通过!")
        print("✓ 行业术语识别功能正常")
        print("✓ QA-SQL检索功能正常")
        print("✓ 相似度计算准确")
        print("✓ 满足验收标准 (≥90%)")
        print("\n下一步: 继续开发后续模块")
        return True
    else:
        print(f"\n⚠️  未达到验收标准 (当前: {success_rate:.1f}%, 要求: ≥90%)")
        print("\n可能的原因:")
        print("1. 术语映射字典不完整")
        print("2. 相似度计算逻辑需要优化")
        print("3. QA存储示例不足")
        return False


if __name__ == "__main__":
    success = test_m6_acceptance()
    sys.exit(0 if success else 1)
