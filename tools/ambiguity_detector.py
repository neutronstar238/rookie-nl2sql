"""
M7: Ambiguity Detector - Detect and clarify ambiguous questions.

This module identifies ambiguous or unclear questions and suggests clarifications.
"""
from typing import Dict, List, Any, Tuple
import re


class AmbiguityDetector:
    """
    Detects ambiguity in natural language questions and suggests clarifications.
    """
    
    def __init__(self):
        # Ambiguous keywords that require clarification
        self.ambiguous_keywords = {
            "最近": ["最近7天", "最近30天", "最近一年"],
            "很多": ["数量 > 10", "数量 > 100", "数量 > 1000"],
            "高": ["价格 > 平均值", "价格 > 10", "价格 > 100"],
            "低": ["价格 < 平均值", "价格 < 10", "价格 < 1"],
            "大量": ["数量 > 100", "数量 > 1000", "数量 > 10000"],
            "popular": ["销量最高", "评分最高", "购买次数最多"],
            "best": ["评分最高", "销量最高", "价格最低"],
            "expensive": ["价格 > 100", "价格 > 平均值", "价格排名前10%"],
            "cheap": ["价格 < 10", "价格 < 平均值", "价格排名后10%"],
            "recent": ["最近7天", "最近30天", "最近一年"],
        }
        
        # Vague quantifiers
        self.vague_quantifiers = [
            "一些", "几个", "很多", "大量", "少量", "some", "few", "many", "several"
        ]
        
        # Missing information patterns
        self.missing_info_patterns = {
            "时间范围": r"(?:查询|统计|显示)(?!.*(?:时间|日期|年|月|日|day|month|year))",
            "排序方式": r"(?:最|top|前)(\d+)(?!.*(?:高|低|新|旧|按|排序|order))",
            "聚合字段": r"(?:统计|总|平均)(?!.*(?:数量|金额|价格|count|sum|avg))",
        }
        
    def detect_ambiguity(self, question: str) -> Dict[str, Any]:
        """
        Detect ambiguity in a question.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with:
            - is_ambiguous: Whether the question is ambiguous
            - ambiguity_score: Ambiguity score (0-1)
            - ambiguity_types: List of detected ambiguity types
            - clarification_questions: Suggested clarification questions
            - normalized_question: Normalized version if possible
        """
        ambiguity_types = []
        clarification_questions = []
        score_components = []
        
        # 1. Check for ambiguous keywords
        keyword_ambiguities = self._check_ambiguous_keywords(question)
        if keyword_ambiguities:
            ambiguity_types.append("ambiguous_keywords")
            clarification_questions.extend(keyword_ambiguities)
            score_components.append(0.3)
        
        # 2. Check for vague quantifiers
        if self._has_vague_quantifiers(question):
            ambiguity_types.append("vague_quantifiers")
            clarification_questions.append("请明确具体的数量范围（例如：大于10，前20个等）")
            score_components.append(0.25)
        
        # 3. Check for missing information
        missing_info = self._check_missing_info(question)
        if missing_info:
            ambiguity_types.extend(missing_info.keys())
            for info_type, suggestion in missing_info.items():
                clarification_questions.append(suggestion)
            score_components.append(0.2 * len(missing_info))
        
        # 4. Check for pronoun references
        if self._has_unclear_pronouns(question):
            ambiguity_types.append("unclear_pronouns")
            clarification_questions.append("请明确指代对象（例如：'它'指代的是什么）")
            score_components.append(0.15)
        
        # 5. Check for multiple interpretations
        interpretations = self._check_multiple_interpretations(question)
        if len(interpretations) > 1:
            ambiguity_types.append("multiple_interpretations")
            clarification_questions.append(f"您是想：{' 或 '.join(interpretations)}？")
            score_components.append(0.25)
        
        # Calculate ambiguity score
        ambiguity_score = min(sum(score_components), 1.0)
        
        # Normalize question if possible
        normalized = self._attempt_normalization(question)
        
        return {
            "is_ambiguous": ambiguity_score > 0.3,
            "ambiguity_score": ambiguity_score,
            "ambiguity_types": ambiguity_types,
            "clarification_questions": clarification_questions,
            "normalized_question": normalized if normalized != question else None,
            "original_question": question
        }
    
    def _check_ambiguous_keywords(self, question: str) -> List[str]:
        """Check for ambiguous keywords and suggest clarifications."""
        suggestions = []
        for keyword, options in self.ambiguous_keywords.items():
            if keyword in question:
                suggestions.append(f"'{keyword}' 有多种理解：{', '.join(options)}，请明确您的意思")
        return suggestions
    
    def _has_vague_quantifiers(self, question: str) -> bool:
        """Check if question contains vague quantifiers."""
        return any(q in question for q in self.vague_quantifiers)
    
    def _check_missing_info(self, question: str) -> Dict[str, str]:
        """Check for missing critical information."""
        missing = {}
        
        # Check time range
        if "最近" in question and not any(t in question for t in ["天", "月", "年", "week", "month", "year"]):
            missing["missing_time_range"] = "请明确时间范围（例如：最近7天、最近一个月）"
        
        # Check sort order for top-N queries
        if re.search(r"(?:前|top)\s*\d+", question) and not any(s in question for s in ["高", "低", "新", "旧", "按", "排序"]):
            missing["missing_sort_order"] = "请明确排序标准（例如：按价格从高到低、按时间从新到旧）"
        
        # Check aggregation field
        if any(w in question for w in ["统计", "总", "平均"]) and not any(f in question for f in ["数量", "金额", "价格", "个数"]):
            missing["missing_aggregation_field"] = "请明确统计字段（例如：数量、金额、价格）"
        
        return missing
    
    def _has_unclear_pronouns(self, question: str) -> bool:
        """Check for unclear pronoun references."""
        pronouns = ["它", "他", "她", "这个", "那个", "它们", "they", "it", "this", "that"]
        # Simple check: if pronoun appears without clear antecedent in first clause
        return any(p in question for p in pronouns) and len(question.split("，")) < 2
    
    def _check_multiple_interpretations(self, question: str) -> List[str]:
        """Check if question has multiple possible interpretations."""
        interpretations = []
        
        # Example: "查询客户订单" could mean customer's orders or order's customers
        if "客户订单" in question:
            interpretations.extend(["查询客户的所有订单", "查询订单对应的客户信息"])
        
        if "产品价格" in question or "歌曲价格" in question:
            interpretations.extend(["查询所有产品的价格列表", "统计产品的平均价格"])
        
        if "销售额" in question and "客户" in question:
            interpretations.extend(["查询每个客户的销售额", "查询销售额最高的客户"])
        
        return interpretations[:2]  # Return max 2 interpretations
    
    def _attempt_normalization(self, question: str) -> str:
        """
        Attempt to normalize ambiguous question with reasonable defaults.
        """
        normalized = question
        
        # Replace ambiguous time references
        normalized = re.sub(r"最近(?![0-9])", "最近30天", normalized)
        
        # Replace vague quantifiers
        vague_map = {
            "很多": "数量 > 100",
            "大量": "数量 > 1000",
            "少量": "数量 < 10",
            "一些": "数量 > 0",
        }
        for vague, specific in vague_map.items():
            if vague in normalized and not any(c.isdigit() for c in normalized):
                # Only replace if no numbers already in question
                normalized = normalized.replace(vague, specific)
        
        return normalized


class ClarificationManager:
    """
    Manages multi-turn clarification dialogs.
    """
    
    def __init__(self):
        self.detector = AmbiguityDetector()
        self.clarification_history = {}
    
    def check_and_clarify(self, question: str, session_id: str = None) -> Dict[str, Any]:
        """
        Check if clarification is needed and manage clarification process.
        
        Args:
            question: Natural language question
            session_id: Optional session ID for tracking multi-turn dialog
            
        Returns:
            Dictionary with:
            - needs_clarification: Whether clarification is needed
            - clarification_questions: List of clarification questions
            - ambiguity_score: Ambiguity score
            - normalized_question: Normalized version
            - can_proceed: Whether we can proceed with current question
        """
        result = self.detector.detect_ambiguity(question)
        
        # Decide if we need clarification
        needs_clarification = result["is_ambiguous"] and result["ambiguity_score"] > 0.5
        
        # If ambiguity is moderate (0.3-0.5), we can try normalized version
        can_proceed = not needs_clarification or result["normalized_question"] is not None
        
        if session_id:
            self.clarification_history[session_id] = {
                "original_question": question,
                "clarification_result": result,
                "timestamp": None
            }
        
        return {
            "needs_clarification": needs_clarification,
            "clarification_questions": result["clarification_questions"][:3],  # Max 3 questions
            "ambiguity_score": result["ambiguity_score"],
            "normalized_question": result["normalized_question"] or question,
            "can_proceed": can_proceed,
            "ambiguity_types": result["ambiguity_types"]
        }


# Singleton instance
clarification_manager = ClarificationManager()


if __name__ == "__main__":
    """Test ambiguity detection."""
    
    print("="*70)
    print("M7 - Ambiguity Detector Test")
    print("="*70)
    
    test_cases = [
        "查询所有客户",  # Clear - no ambiguity
        "查询最近的订单",  # Ambiguous - "最近" undefined
        "查询销售额很多的客户",  # Ambiguous - "很多" vague
        "查询前10个客户",  # Ambiguous - missing sort criteria
        "查询客户订单",  # Ambiguous - multiple interpretations
        "统计每个国家的客户数量",  # Clear
        "查询价格高的产品",  # Ambiguous - "高" undefined
        "查询2024年1月销售额超过1000的客户",  # Clear
    ]
    
    manager = ClarificationManager()
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n### Test Case {i} ###")
        print(f"Question: {question}")
        
        result = manager.check_and_clarify(question, session_id=f"test_{i}")
        
        print(f"Needs Clarification: {'Yes' if result['needs_clarification'] else 'No'}")
        print(f"Ambiguity Score: {result['ambiguity_score']:.2f}")
        print(f"Can Proceed: {'Yes' if result['can_proceed'] else 'No'}")
        
        if result['clarification_questions']:
            print(f"Clarification Questions:")
            for q in result['clarification_questions']:
                print(f"  - {q}")
        
        if result['normalized_question'] != question:
            print(f"Normalized: {result['normalized_question']}")
        
        print(f"Ambiguity Types: {', '.join(result['ambiguity_types']) if result['ambiguity_types'] else 'None'}")
    
    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70)
