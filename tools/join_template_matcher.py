"""
M8: Join Template Matcher - Few-shot templates for complex multi-table JOIN queries.

This module provides pre-defined templates for common JOIN patterns and matches
them to user questions to improve SQL generation quality.
"""
from typing import Dict, List, Any, Tuple
import re


class JoinTemplate:
    """Represents a reusable JOIN template."""
    
    def __init__(
        self,
        template_id: str,
        name: str,
        description: str,
        pattern: str,
        tables: List[str],
        sql_template: str,
        example_question: str,
        example_sql: str,
        complexity: str = "simple"
    ):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.pattern = pattern  # Regex pattern to match questions
        self.tables = tables
        self.sql_template = sql_template
        self.example_question = example_question
        self.example_sql = example_sql
        self.complexity = complexity  # simple, medium, complex
    
    def matches(self, question: str) -> float:
        """
        Check if this template matches the question.
        
        Returns:
            Match score (0-1)
        """
        # Pattern matching
        pattern_match = bool(re.search(self.pattern, question, re.IGNORECASE))
        
        # Table name matching
        table_matches = sum(1 for table in self.tables if table.lower() in question.lower())
        table_score = table_matches / len(self.tables) if self.tables else 0
        
        # Combine scores
        if pattern_match and table_score > 0.5:
            return 0.8 + (table_score * 0.2)
        elif pattern_match:
            return 0.6
        elif table_score > 0.5:
            return 0.5 + (table_score * 0.3)
        else:
            return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "tables": self.tables,
            "example_question": self.example_question,
            "example_sql": self.example_sql,
            "complexity": self.complexity
        }


class JoinTemplateLibrary:
    """Library of JOIN templates for Chinook database."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> List[JoinTemplate]:
        """Initialize template library with common JOIN patterns."""
        
        templates = [
            # Template 1: Customer -> Invoice (1:N)
            JoinTemplate(
                template_id="customer_invoice",
                name="客户订单关联",
                description="关联客户和其订单/发票",
                pattern=r"客户.*(?:订单|发票|消费|购买)|(?:订单|发票).*客户",
                tables=["Customer", "Invoice"],
                sql_template="""
SELECT c.FirstName, c.LastName, i.InvoiceId, i.Total, i.InvoiceDate
FROM Customer c
JOIN Invoice i ON c.CustomerId = i.CustomerId
WHERE {conditions}
ORDER BY {order_by}
                """.strip(),
                example_question="查询每个客户的订单总额",
                example_sql="""
SELECT c.FirstName, c.LastName, SUM(i.Total) as TotalAmount
FROM Customer c
JOIN Invoice i ON c.CustomerId = i.CustomerId
GROUP BY c.CustomerId, c.FirstName, c.LastName
ORDER BY TotalAmount DESC;
                """.strip(),
                complexity="simple"
            ),
            
            # Template 2: Album -> Artist (N:1)
            JoinTemplate(
                template_id="album_artist",
                name="专辑艺术家关联",
                description="关联专辑和艺术家",
                pattern=r"(?:专辑|album).*(?:艺术家|artist)|(?:艺术家|artist).*(?:专辑|album)",
                tables=["Album", "Artist"],
                sql_template="""
SELECT al.Title, ar.Name as ArtistName
FROM Album al
JOIN Artist ar ON al.ArtistId = ar.ArtistId
WHERE {conditions}
ORDER BY {order_by}
                """.strip(),
                example_question="查询所有专辑及其艺术家",
                example_sql="""
SELECT al.Title, ar.Name as ArtistName
FROM Album al
JOIN Artist ar ON al.ArtistId = ar.ArtistId
ORDER BY ar.Name, al.Title;
                """.strip(),
                complexity="simple"
            ),
            
            # Template 3: Track -> Album -> Artist (Chain)
            JoinTemplate(
                template_id="track_album_artist",
                name="歌曲-专辑-艺术家链",
                description="三表关联：歌曲到专辑到艺术家",
                pattern=r"(?:歌曲|track).*(?:艺术家|artist)|(?:艺术家|artist).*(?:歌曲|track)",
                tables=["Track", "Album", "Artist"],
                sql_template="""
SELECT t.Name as TrackName, al.Title as AlbumTitle, ar.Name as ArtistName
FROM Track t
JOIN Album al ON t.AlbumId = al.AlbumId
JOIN Artist ar ON al.ArtistId = ar.ArtistId
WHERE {conditions}
ORDER BY {order_by}
                """.strip(),
                example_question="查询所有歌曲及其艺术家",
                example_sql="""
SELECT t.Name as TrackName, ar.Name as ArtistName, t.Milliseconds
FROM Track t
JOIN Album al ON t.AlbumId = al.AlbumId
JOIN Artist ar ON al.ArtistId = ar.ArtistId
ORDER BY ar.Name, t.Name;
                """.strip(),
                complexity="medium"
            ),
            
            # Template 4: Track -> Genre (N:1 with grouping)
            JoinTemplate(
                template_id="track_genre_stats",
                name="歌曲分类统计",
                description="按音乐风格统计歌曲",
                pattern=r"(?:风格|genre|分类).*(?:歌曲|track|统计|数量)",
                tables=["Track", "Genre"],
                sql_template="""
SELECT g.Name as GenreName, COUNT(*) as TrackCount, AVG(t.Milliseconds) as AvgDuration
FROM Track t
JOIN Genre g ON t.GenreId = g.GenreId
GROUP BY g.GenreId, g.Name
ORDER BY {order_by}
                """.strip(),
                example_question="统计每个音乐风格的歌曲数量",
                example_sql="""
SELECT g.Name as GenreName, COUNT(*) as TrackCount
FROM Track t
JOIN Genre g ON t.GenreId = g.GenreId
GROUP BY g.GenreId, g.Name
ORDER BY TrackCount DESC;
                """.strip(),
                complexity="simple"
            ),
            
            # Template 5: Invoice -> InvoiceLine -> Track (Complex aggregation)
            JoinTemplate(
                template_id="invoice_track_sales",
                name="销售明细分析",
                description="订单明细关联到商品",
                pattern=r"(?:畅销|热门|最多|销量|销售.*(?:歌曲|商品))|(?:歌曲|商品).*销售",
                tables=["Invoice", "InvoiceLine", "Track"],
                sql_template="""
SELECT t.Name, COUNT(*) as SalesCount, SUM(il.Quantity) as TotalQuantity, SUM(il.UnitPrice * il.Quantity) as Revenue
FROM Invoice i
JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
JOIN Track t ON il.TrackId = t.TrackId
GROUP BY t.TrackId, t.Name
ORDER BY {order_by}
                """.strip(),
                example_question="查询最畅销的歌曲",
                example_sql="""
SELECT t.Name, COUNT(*) as SalesCount, SUM(il.UnitPrice * il.Quantity) as Revenue
FROM InvoiceLine il
JOIN Track t ON il.TrackId = t.TrackId
GROUP BY t.TrackId, t.Name
ORDER BY SalesCount DESC
LIMIT 10;
                """.strip(),
                complexity="complex"
            ),
            
            # Template 6: Customer -> Invoice -> InvoiceLine -> Track (4-table join)
            JoinTemplate(
                template_id="customer_purchase_history",
                name="客户购买历史",
                description="客户购买的具体歌曲",
                pattern=r"客户.*购买.*(?:歌曲|track|音乐)|(?:购买|买).*(?:歌曲|track).*客户",
                tables=["Customer", "Invoice", "InvoiceLine", "Track"],
                sql_template="""
SELECT c.FirstName, c.LastName, t.Name as TrackName, i.InvoiceDate, il.UnitPrice
FROM Customer c
JOIN Invoice i ON c.CustomerId = i.CustomerId
JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
JOIN Track t ON il.TrackId = t.TrackId
WHERE {conditions}
ORDER BY {order_by}
                """.strip(),
                example_question="查询客户购买的所有歌曲",
                example_sql="""
SELECT c.FirstName, c.LastName, t.Name as TrackName, i.InvoiceDate
FROM Customer c
JOIN Invoice i ON c.CustomerId = i.CustomerId
JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
JOIN Track t ON il.TrackId = t.TrackId
ORDER BY c.LastName, i.InvoiceDate;
                """.strip(),
                complexity="complex"
            ),
            
            # Template 7: Playlist -> PlaylistTrack -> Track (Many-to-Many)
            JoinTemplate(
                template_id="playlist_tracks",
                name="播放列表歌曲",
                description="播放列表包含的歌曲（多对多）",
                pattern=r"(?:播放列表|playlist).*(?:歌曲|track)",
                tables=["Playlist", "PlaylistTrack", "Track"],
                sql_template="""
SELECT p.Name as PlaylistName, t.Name as TrackName, t.Milliseconds, t.UnitPrice
FROM Playlist p
JOIN PlaylistTrack pt ON p.PlaylistId = pt.PlaylistId
JOIN Track t ON pt.TrackId = t.TrackId
WHERE {conditions}
ORDER BY {order_by}
                """.strip(),
                example_question="查询播放列表中的所有歌曲",
                example_sql="""
SELECT p.Name as PlaylistName, COUNT(*) as TrackCount
FROM Playlist p
JOIN PlaylistTrack pt ON p.PlaylistId = pt.PlaylistId
GROUP BY p.PlaylistId, p.Name
ORDER BY TrackCount DESC;
                """.strip(),
                complexity="medium"
            ),
            
            # Template 8: Employee hierarchy (Self-join)
            JoinTemplate(
                template_id="employee_hierarchy",
                name="员工层级关系",
                description="员工上下级关系（自连接）",
                pattern=r"(?:员工|employee).*(?:上级|下级|经理|manager|层级)",
                tables=["Employee"],
                sql_template="""
SELECT e.FirstName || ' ' || e.LastName as EmployeeName,
       m.FirstName || ' ' || m.LastName as ManagerName
FROM Employee e
LEFT JOIN Employee m ON e.ReportsTo = m.EmployeeId
ORDER BY {order_by}
                """.strip(),
                example_question="查询员工及其直接上级",
                example_sql="""
SELECT e.FirstName || ' ' || e.LastName as EmployeeName,
       m.FirstName || ' ' || m.LastName as ManagerName
FROM Employee e
LEFT JOIN Employee m ON e.ReportsTo = m.EmployeeId
ORDER BY e.LastName;
                """.strip(),
                complexity="medium"
            ),
            
            # Template 9: Customer country statistics
            JoinTemplate(
                template_id="country_sales_stats",
                name="国家销售统计",
                description="按国家统计客户和销售",
                pattern=r"(?:国家|country).*(?:统计|销售|客户)",
                tables=["Customer", "Invoice"],
                sql_template="""
SELECT c.Country, COUNT(DISTINCT c.CustomerId) as CustomerCount, 
       COUNT(i.InvoiceId) as OrderCount, SUM(i.Total) as TotalRevenue
FROM Customer c
LEFT JOIN Invoice i ON c.CustomerId = i.CustomerId
GROUP BY c.Country
ORDER BY {order_by}
                """.strip(),
                example_question="统计每个国家的客户数和销售额",
                example_sql="""
SELECT c.Country, COUNT(DISTINCT c.CustomerId) as CustomerCount, 
       COALESCE(SUM(i.Total), 0) as TotalRevenue
FROM Customer c
LEFT JOIN Invoice i ON c.CustomerId = i.CustomerId
GROUP BY c.Country
ORDER BY TotalRevenue DESC;
                """.strip(),
                complexity="medium"
            ),
            
            # Template 10: Complex: Top customers by genre
            JoinTemplate(
                template_id="customer_genre_preference",
                name="客户音乐偏好",
                description="客户最喜欢的音乐风格",
                pattern=r"客户.*(?:偏好|喜欢|风格|genre)",
                tables=["Customer", "Invoice", "InvoiceLine", "Track", "Genre"],
                sql_template="""
SELECT c.FirstName, c.LastName, g.Name as GenreName, 
       COUNT(*) as PurchaseCount, SUM(il.UnitPrice * il.Quantity) as TotalSpent
FROM Customer c
JOIN Invoice i ON c.CustomerId = i.CustomerId
JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
JOIN Track t ON il.TrackId = t.TrackId
JOIN Genre g ON t.GenreId = g.GenreId
GROUP BY c.CustomerId, c.FirstName, c.LastName, g.GenreId, g.Name
ORDER BY {order_by}
                """.strip(),
                example_question="查询每个客户最喜欢的音乐风格",
                example_sql="""
SELECT c.FirstName, c.LastName, g.Name as FavoriteGenre, COUNT(*) as PurchaseCount
FROM Customer c
JOIN Invoice i ON c.CustomerId = i.CustomerId
JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
JOIN Track t ON il.TrackId = t.TrackId
JOIN Genre g ON t.GenreId = g.GenreId
GROUP BY c.CustomerId, c.FirstName, c.LastName, g.GenreId, g.Name
ORDER BY c.CustomerId, PurchaseCount DESC;
                """.strip(),
                complexity="complex"
            ),
        ]
        
        return templates
    
    def find_matching_templates(self, question: str, top_k: int = 3) -> List[Tuple[JoinTemplate, float]]:
        """
        Find templates that match the question.
        
        Args:
            question: Natural language question
            top_k: Number of top matches to return
            
        Returns:
            List of (template, score) tuples, sorted by score
        """
        matches = []
        
        for template in self.templates:
            score = template.matches(question)
            if score > 0.3:  # Minimum threshold
                matches.append((template, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:top_k]
    
    def get_template_by_id(self, template_id: str) -> JoinTemplate:
        """Get template by ID."""
        for template in self.templates:
            if template.template_id == template_id:
                return template
        return None
    
    def analyze_join_complexity(self, question: str) -> Dict[str, Any]:
        """
        Analyze the JOIN complexity of a question.
        
        Returns:
            Dictionary with:
            - complexity: simple/medium/complex
            - table_count: Estimated number of tables
            - join_type: inner/left/self
            - suggested_templates: Matching templates
        """
        # Find matching templates
        matches = self.find_matching_templates(question, top_k=3)
        
        if not matches:
            # No template match - analyze manually
            table_count = self._estimate_table_count(question)
            complexity = self._classify_complexity(table_count, question)
            
            return {
                "complexity": complexity,
                "table_count": table_count,
                "join_type": "inner",
                "suggested_templates": [],
                "has_template": False
            }
        
        # Use best match
        best_template, best_score = matches[0]
        
        return {
            "complexity": best_template.complexity,
            "table_count": len(best_template.tables),
            "join_type": self._infer_join_type(question),
            "suggested_templates": [
                {
                    "template_id": t.template_id,
                    "name": t.name,
                    "score": score,
                    "example": t.example_sql
                }
                for t, score in matches
            ],
            "has_template": True,
            "best_match": best_template.to_dict()
        }
    
    def _estimate_table_count(self, question: str) -> int:
        """Estimate number of tables needed."""
        # Simple heuristic based on keywords
        table_keywords = ["customer", "invoice", "track", "album", "artist", "genre", "playlist", "employee"]
        chinese_keywords = ["客户", "订单", "发票", "歌曲", "专辑", "艺术家", "风格", "播放列表", "员工"]
        
        count = 0
        for kw in table_keywords + chinese_keywords:
            if kw in question.lower():
                count += 1
        
        return max(count, 1)
    
    def _classify_complexity(self, table_count: int, question: str) -> str:
        """Classify JOIN complexity."""
        if table_count <= 2:
            return "simple"
        elif table_count <= 3:
            return "medium"
        else:
            return "complex"
    
    def _infer_join_type(self, question: str) -> str:
        """Infer JOIN type from question."""
        if any(kw in question.lower() for kw in ["所有", "包括", "含", "all", "include"]):
            return "left"
        elif any(kw in question.lower() for kw in ["上级", "下级", "层级", "manager", "hierarchy"]):
            return "self"
        else:
            return "inner"


# Singleton instance
join_template_library = JoinTemplateLibrary()


if __name__ == "__main__":
    """Test join template matcher."""
    
    print("="*70)
    print("M8 - Join Template Matcher Test")
    print("="*70)
    
    test_questions = [
        "查询每个客户的订单总额",
        "查询所有专辑及其艺术家",
        "查询所有歌曲及其艺术家",
        "统计每个音乐风格的歌曲数量",
        "查询最畅销的歌曲",
        "查询客户购买的所有歌曲",
        "查询播放列表中的所有歌曲",
        "查询员工及其直接上级",
        "统计每个国家的客户数和销售额",
        "查询每个客户最喜欢的音乐风格",
    ]
    
    library = join_template_library
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n### Test {i}: {question} ###")
        
        analysis = library.analyze_join_complexity(question)
        
        print(f"Complexity: {analysis['complexity']}")
        print(f"Estimated Tables: {analysis['table_count']}")
        print(f"Join Type: {analysis['join_type']}")
        print(f"Has Template: {analysis['has_template']}")
        
        if analysis['suggested_templates']:
            print(f"Suggested Templates:")
            for template in analysis['suggested_templates'][:2]:
                print(f"  - {template['name']} (score: {template['score']:.2f})")
        
        if analysis.get('best_match'):
            best = analysis['best_match']
            print(f"\nBest Match: {best['name']}")
            print(f"Example SQL:\n{best['example_sql'][:150]}...")
    
    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70)
