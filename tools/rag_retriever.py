"""
RAG (Retrieval-Augmented Generation) Retriever for NL2SQL system.
M6: Implements domain-specific terminology recognition and historical QA-SQL retrieval.
"""
import sys
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DomainTerminologyMapper:
    """
    Maps domain-specific terminology (行业黑话) to database schema.
    
    Examples:
    - "销售额" → SUM(Invoice.Total)
    - "客户" → Customer table
    - "歌曲" → Track table
    """
    
    def __init__(self, terminology_file: Optional[str] = None):
        """
        Initialize terminology mapper.
        
        Args:
            terminology_file: Path to terminology mapping JSON file
        """
        self.mappings = self._load_default_mappings()
        
        if terminology_file and Path(terminology_file).exists():
            custom_mappings = self._load_custom_mappings(terminology_file)
            self.mappings.update(custom_mappings)
    
    def _load_default_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load default domain terminology mappings for Chinook database."""
        return {
            # Table mappings
            "客户": {
                "type": "table",
                "target": "Customer",
                "description": "客户信息表"
            },
            "顾客": {
                "type": "table",
                "target": "Customer",
                "description": "客户信息表"
            },
            "订单": {
                "type": "table",
                "target": "Invoice",
                "description": "订单/发票表"
            },
            "发票": {
                "type": "table",
                "target": "Invoice",
                "description": "订单/发票表"
            },
            "歌曲": {
                "type": "table",
                "target": "Track",
                "description": "歌曲/曲目表"
            },
            "曲目": {
                "type": "table",
                "target": "Track",
                "description": "歌曲/曲目表"
            },
            "产品": {
                "type": "table",
                "target": "Track",
                "description": "产品(歌曲)表"
            },
            "专辑": {
                "type": "table",
                "target": "Album",
                "description": "专辑表"
            },
            "艺术家": {
                "type": "table",
                "target": "Artist",
                "description": "艺术家表"
            },
            "歌手": {
                "type": "table",
                "target": "Artist",
                "description": "艺术家/歌手表"
            },
            "分类": {
                "type": "table",
                "target": "Genre",
                "description": "音乐分类/风格表"
            },
            "类别": {
                "type": "table",
                "target": "Genre",
                "description": "音乐分类/风格表"
            },
            "风格": {
                "type": "table",
                "target": "Genre",
                "description": "音乐风格表"
            },
            
            # Column mappings
            "价格": {
                "type": "column",
                "target": "UnitPrice",
                "table": "Track",
                "description": "歌曲单价"
            },
            "单价": {
                "type": "column",
                "target": "UnitPrice",
                "table": "Track",
                "description": "歌曲单价"
            },
            "金额": {
                "type": "column",
                "target": "Total",
                "table": "Invoice",
                "description": "订单总金额"
            },
            "总额": {
                "type": "column",
                "target": "Total",
                "table": "Invoice",
                "description": "订单总金额"
            },
            "城市": {
                "type": "column",
                "target": "City",
                "table": "Customer",
                "description": "客户所在城市"
            },
            "国家": {
                "type": "column",
                "target": "Country",
                "table": "Customer",
                "description": "客户所在国家"
            },
            "姓名": {
                "type": "column",
                "target": "FirstName, LastName",
                "table": "Customer",
                "description": "客户姓名"
            },
            "名字": {
                "type": "column",
                "target": "FirstName, LastName",
                "table": "Customer",
                "description": "客户姓名"
            },
            
            # Aggregate function mappings
            "销售额": {
                "type": "aggregate",
                "target": "SUM(Invoice.Total)",
                "description": "总销售额"
            },
            "营业额": {
                "type": "aggregate",
                "target": "SUM(Invoice.Total)",
                "description": "总营业额"
            },
            "收入": {
                "type": "aggregate",
                "target": "SUM(Invoice.Total)",
                "description": "总收入"
            },
            "平均价格": {
                "type": "aggregate",
                "target": "AVG(Track.UnitPrice)",
                "description": "平均歌曲价格"
            },
            "最高价": {
                "type": "aggregate",
                "target": "MAX(Track.UnitPrice)",
                "description": "最高价格"
            },
            "最低价": {
                "type": "aggregate",
                "target": "MIN(Track.UnitPrice)",
                "description": "最低价格"
            }
        }
    
    def _load_custom_mappings(self, filepath: str) -> Dict[str, Dict[str, Any]]:
        """Load custom terminology mappings from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load custom mappings from {filepath}: {e}")
            return {}
    
    def recognize_terms(self, question: str) -> List[Dict[str, Any]]:
        """
        Recognize domain-specific terms in a question.
        
        Args:
            question: Natural language question
            
        Returns:
            List of recognized terms with their mappings
        """
        recognized = []
        
        for term, mapping in self.mappings.items():
            if term in question:
                recognized.append({
                    "term": term,
                    "type": mapping["type"],
                    "target": mapping["target"],
                    "description": mapping.get("description", ""),
                    "table": mapping.get("table", "")
                })
        
        return recognized
    
    def get_mapping_hint(self, question: str) -> str:
        """
        Generate mapping hints for SQL generation.
        
        Args:
            question: Natural language question
            
        Returns:
            Formatted hint string for LLM
        """
        recognized = self.recognize_terms(question)
        
        if not recognized:
            return ""
        
        hints = ["检测到的行业术语映射："]
        
        for item in recognized:
            if item["type"] == "table":
                hints.append(f"  - '{item['term']}' → {item['target']} 表")
            elif item["type"] == "column":
                hints.append(f"  - '{item['term']}' → {item['target']} 列 ({item['table']} 表)")
            elif item["type"] == "aggregate":
                hints.append(f"  - '{item['term']}' → {item['target']}")
        
        return "\n".join(hints)


class QASQLStore:
    """
    Stores and retrieves historical Question-Answer-SQL pairs.
    
    Features:
    - Store successful QA-SQL pairs
    - Retrieve similar questions
    - Simple similarity matching (can be upgraded to vector search)
    """
    
    def __init__(self, store_file: Optional[str] = None):
        """
        Initialize QA-SQL store.
        
        Args:
            store_file: Path to store file (JSON format)
        """
        self.store_file = store_file or str(project_root / "data" / "qa_sql_store.json")
        self.store: List[Dict[str, Any]] = self._load_store()
    
    def _load_store(self) -> List[Dict[str, Any]]:
        """Load QA-SQL pairs from file."""
        if Path(self.store_file).exists():
            try:
                with open(self.store_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load QA-SQL store: {e}")
        
        # Return default examples if file doesn't exist
        return self._get_default_examples()
    
    def _get_default_examples(self) -> List[Dict[str, Any]]:
        """Get default QA-SQL examples for Chinook database."""
        return [
            {
                "id": 1,
                "question": "查询所有客户",
                "sql": "SELECT * FROM Customer LIMIT 100;",
                "success": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 2,
                "question": "统计每个国家的客户数量",
                "sql": "SELECT Country, COUNT(*) as CustomerCount FROM Customer GROUP BY Country ORDER BY CustomerCount DESC LIMIT 100;",
                "success": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 3,
                "question": "查询销售额最高的前10个客户",
                "sql": "SELECT c.FirstName, c.LastName, SUM(i.Total) as TotalSales FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId GROUP BY c.CustomerId, c.FirstName, c.LastName ORDER BY TotalSales DESC LIMIT 10;",
                "success": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 4,
                "question": "统计每个音乐风格的歌曲数量",
                "sql": "SELECT g.Name, COUNT(*) as TrackCount FROM Track t JOIN Genre g ON t.GenreId = g.GenreId GROUP BY g.GenreId, g.Name ORDER BY TrackCount DESC LIMIT 100;",
                "success": True,
                "created_at": "2025-01-01T00:00:00"
            },
            {
                "id": 5,
                "question": "查询价格在0.99到1.99之间的歌曲",
                "sql": "SELECT Name, UnitPrice FROM Track WHERE UnitPrice BETWEEN 0.99 AND 1.99 LIMIT 100;",
                "success": True,
                "created_at": "2025-01-01T00:00:00"
            }
        ]
    
    def _save_store(self):
        """Save QA-SQL pairs to file."""
        try:
            # Ensure directory exists
            Path(self.store_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.store_file, 'w', encoding='utf-8') as f:
                json.dump(self.store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save QA-SQL store: {e}")
    
    def add(self, question: str, sql: str, success: bool = True):
        """
        Add a new QA-SQL pair to the store.
        
        Args:
            question: Natural language question
            sql: Corresponding SQL query
            success: Whether the SQL executed successfully
        """
        new_id = max([item["id"] for item in self.store], default=0) + 1
        
        self.store.append({
            "id": new_id,
            "question": question,
            "sql": sql,
            "success": success,
            "created_at": datetime.now().isoformat()
        })
        
        self._save_store()
    
    def retrieve_similar(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve similar QA-SQL pairs.
        
        Args:
            question: Query question
            top_k: Number of similar pairs to return
            
        Returns:
            List of similar QA-SQL pairs with similarity scores
        """
        # Simple keyword-based similarity (can be upgraded to embedding-based)
        results = []
        
        for item in self.store:
            if not item.get("success", True):
                continue  # Skip failed queries
            
            similarity = self._calculate_similarity(question, item["question"])
            
            results.append({
                **item,
                "similarity": similarity
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results[:top_k]
    
    def _calculate_similarity(self, q1: str, q2: str) -> float:
        """
        Calculate similarity between two questions.
        
        Simple keyword-based similarity:
        - Common keywords count / total unique keywords
        
        Can be upgraded to:
        - TF-IDF cosine similarity
        - Sentence embeddings cosine similarity
        - Edit distance
        """
        # Tokenize
        tokens1 = set(self._tokenize(q1))
        tokens2 = set(self._tokenize(q2))
        
        # Calculate Jaccard similarity
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        return len(intersection) / len(union)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for Chinese and English text."""
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split by whitespace
        tokens = text.lower().split()
        
        # For Chinese, also split into characters
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        
        return tokens + chinese_chars


class RAGRetriever:
    """
    Main RAG retriever combining terminology mapping and QA-SQL retrieval.
    """
    
    def __init__(
        self,
        terminology_file: Optional[str] = None,
        qa_store_file: Optional[str] = None
    ):
        """
        Initialize RAG retriever.
        
        Args:
            terminology_file: Custom terminology mapping file
            qa_store_file: QA-SQL store file
        """
        self.terminology_mapper = DomainTerminologyMapper(terminology_file)
        self.qa_store = QASQLStore(qa_store_file)
    
    def retrieve(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieve RAG evidence for a question.
        
        Args:
            question: Natural language question
            top_k: Number of similar QA pairs to retrieve
            
        Returns:
            Dictionary with:
            - terminology_hints: Recognized domain terms
            - similar_examples: Similar QA-SQL pairs
            - has_evidence: Whether any evidence was found
        """
        # Recognize terminology
        recognized_terms = self.terminology_mapper.recognize_terms(question)
        terminology_hints = self.terminology_mapper.get_mapping_hint(question)
        
        # Retrieve similar QA pairs
        similar_examples = self.qa_store.retrieve_similar(question, top_k=top_k)
        
        # Filter out examples with very low similarity (< 0.1)
        meaningful_examples = [ex for ex in similar_examples if ex.get('similarity', 0) >= 0.1]
        
        return {
            "terminology_hints": terminology_hints,
            "recognized_terms": recognized_terms,
            "similar_examples": similar_examples,  # Keep all for reference
            "has_evidence": bool(recognized_terms) or bool(meaningful_examples),
            "retrieved_at": datetime.now().isoformat()
        }
    
    def add_successful_query(self, question: str, sql: str):
        """
        Add a successful query to the QA store for future retrieval.
        
        Args:
            question: Natural language question
            sql: Successful SQL query
        """
        self.qa_store.add(question, sql, success=True)


# Global RAG retriever instance
rag_retriever = RAGRetriever()


if __name__ == "__main__":
    """Test RAG Retriever"""
    print("=== RAG Retriever Test ===\n")
    
    test_questions = [
        "查询所有客户的姓名和城市",
        "统计每个国家的客户数量",
        "查询销售额最高的前10个客户",
        "统计每个音乐风格的歌曲平均价格",
        "查询价格在1到2元之间的产品"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {question}")
        print(f"{'='*60}")
        
        result = rag_retriever.retrieve(question, top_k=2)
        
        print(f"\n✓ Evidence Found: {result['has_evidence']}")
        
        if result['terminology_hints']:
            print(f"\n{result['terminology_hints']}")
        
        if result['similar_examples']:
            print(f"\n相似历史查询 (Top {len(result['similar_examples'])}):")
            for j, example in enumerate(result['similar_examples'], 1):
                print(f"\n  {j}. 问题: {example['question']}")
                print(f"     相似度: {example['similarity']:.2f}")
                print(f"     SQL: {example['sql'][:80]}...")
    
    print(f"\n{'='*60}")
    print("Test Complete!")
    print(f"{'='*60}")
