"""
SQL Execution Sandbox for security and risk management.
M5: Protects database from dangerous queries and limits execution risks.
"""
import re
import time
from typing import Dict, Any, List, Tuple, Optional


class SQLSandbox:
    """
    SQL Execution Sandbox that checks and limits SQL queries before execution.
    
    Features:
    - Dangerous operation detection (DROP, DELETE, UPDATE, etc.)
    - Row limit enforcement
    - Timeout estimation
    - Query complexity analysis
    - Resource usage limits
    """
    
    def __init__(
        self,
        max_rows: int = 1000,
        max_timeout_seconds: int = 30,
        allow_write: bool = False,
        allow_ddl: bool = False
    ):
        """
        Initialize sandbox with security policies.
        
        Args:
            max_rows: Maximum rows allowed to return
            max_timeout_seconds: Maximum query execution time
            allow_write: Allow INSERT/UPDATE/DELETE operations
            allow_ddl: Allow DDL operations (CREATE/DROP/ALTER)
        """
        self.max_rows = max_rows
        self.max_timeout_seconds = max_timeout_seconds
        self.allow_write = allow_write
        self.allow_ddl = allow_ddl
        
        # Dangerous keywords that require special permission
        self.ddl_keywords = [
            "DROP", "CREATE", "ALTER", "TRUNCATE", "RENAME"
        ]
        
        self.dml_write_keywords = [
            "INSERT", "UPDATE", "DELETE", "REPLACE", "MERGE"
        ]
        
        self.dangerous_keywords = [
            "EXEC", "EXECUTE", "PRAGMA", "ATTACH", "DETACH"
        ]
    
    def check_sql(self, sql: str) -> Dict[str, Any]:
        """
        Perform comprehensive security check on SQL query.
        
        Args:
            sql: SQL query string
            
        Returns:
            Dictionary with:
            - allowed: bool - whether query is allowed
            - risk_level: str - "safe", "low", "medium", "high", "critical"
            - issues: list - list of security issues found
            - warnings: list - list of warnings
            - modifications: dict - suggested modifications
            - estimated_timeout: float - estimated execution time in seconds
        """
        result = {
            "allowed": True,
            "risk_level": "safe",
            "issues": [],
            "warnings": [],
            "modifications": {},
            "estimated_timeout": 0.0,
            "original_sql": sql,
            "safe_sql": sql
        }
        
        if not sql or not sql.strip():
            result["allowed"] = False
            result["risk_level"] = "critical"
            result["issues"].append("Empty SQL query")
            return result
        
        sql_upper = sql.strip().upper()
        sql_normalized = " ".join(sql_upper.split())
        
        # Check 1: DDL operations
        ddl_found = [kw for kw in self.ddl_keywords if kw in sql_normalized]
        if ddl_found:
            if not self.allow_ddl:
                result["allowed"] = False
                result["risk_level"] = "critical"
                result["issues"].append(f"DDL operations not allowed: {', '.join(ddl_found)}")
            else:
                result["risk_level"] = "high"
                result["warnings"].append(f"DDL operation detected: {', '.join(ddl_found)}")
        
        # Check 2: Write operations
        write_found = [kw for kw in self.dml_write_keywords if kw in sql_normalized]
        if write_found:
            if not self.allow_write:
                result["allowed"] = False
                result["risk_level"] = "critical"
                result["issues"].append(f"Write operations not allowed: {', '.join(write_found)}")
            else:
                result["risk_level"] = "high"
                result["warnings"].append(f"Write operation detected: {', '.join(write_found)}")
        
        # Check 3: Dangerous functions
        dangerous_found = [kw for kw in self.dangerous_keywords if kw in sql_normalized]
        if dangerous_found:
            result["allowed"] = False
            result["risk_level"] = "critical"
            result["issues"].append(f"Dangerous operations detected: {', '.join(dangerous_found)}")
        
        # Check 4: Multiple statements (SQL injection risk)
        if self._has_multiple_statements(sql):
            result["allowed"] = False
            result["risk_level"] = "critical"
            result["issues"].append("Multiple SQL statements detected (SQL injection risk)")
        
        # Check 5: LIMIT clause enforcement (for SELECT queries)
        if sql_upper.startswith("SELECT") and not result["issues"]:
            has_limit, current_limit = self._check_limit_clause(sql)
            
            if not has_limit:
                # Add LIMIT clause
                result["warnings"].append(f"No LIMIT clause found, adding LIMIT {self.max_rows}")
                result["modifications"]["limit_added"] = True
                result["safe_sql"] = self._add_limit_clause(sql, self.max_rows)
            elif current_limit > self.max_rows:
                # Reduce LIMIT
                result["warnings"].append(f"LIMIT {current_limit} exceeds maximum {self.max_rows}, reducing")
                result["modifications"]["limit_reduced"] = True
                result["safe_sql"] = self._reduce_limit_clause(sql, self.max_rows)
        
        # Check 6: Query complexity
        complexity = self._estimate_complexity(sql)
        result["estimated_timeout"] = complexity["estimated_time"]
        
        if complexity["complexity_level"] == "high":
            result["risk_level"] = "medium"
            result["warnings"].append(f"High complexity query: {complexity['reason']}")
        
        if complexity["estimated_time"] > self.max_timeout_seconds:
            result["allowed"] = False
            result["risk_level"] = "high"
            result["issues"].append(
                f"Estimated timeout ({complexity['estimated_time']}s) exceeds limit ({self.max_timeout_seconds}s)"
            )
        
        # Check 7: Subquery depth
        subquery_depth = self._count_subquery_depth(sql)
        if subquery_depth > 3:
            result["risk_level"] = "medium"
            result["warnings"].append(f"Deep subquery nesting (depth: {subquery_depth})")
        
        return result
    
    def _has_multiple_statements(self, sql: str) -> bool:
        """Check if SQL contains multiple statements (semicolon-separated)."""
        # Remove strings to avoid false positives
        cleaned = re.sub(r"'[^']*'", "", sql)
        cleaned = re.sub(r'"[^"]*"', "", cleaned)
        
        # Check for semicolons (allow trailing semicolon)
        semicolons = cleaned.count(";")
        if semicolons > 1:
            return True
        if semicolons == 1 and not cleaned.strip().endswith(";"):
            return True
        
        return False
    
    def _check_limit_clause(self, sql: str) -> Tuple[bool, Optional[int]]:
        """
        Check if SQL has LIMIT clause and extract the limit value.
        
        Returns:
            (has_limit, limit_value)
        """
        # Match LIMIT with optional OFFSET
        limit_pattern = r'\bLIMIT\s+(\d+)'
        match = re.search(limit_pattern, sql, re.IGNORECASE)
        
        if match:
            limit_value = int(match.group(1))
            return (True, limit_value)
        
        return (False, None)
    
    def _add_limit_clause(self, sql: str, limit: int) -> str:
        """Add LIMIT clause to SQL query."""
        sql = sql.strip()
        
        # Remove trailing semicolon if present
        if sql.endswith(";"):
            sql = sql[:-1].strip()
        
        # Add LIMIT
        sql = f"{sql} LIMIT {limit};"
        
        return sql
    
    def _reduce_limit_clause(self, sql: str, max_limit: int) -> str:
        """Reduce existing LIMIT clause to max_limit."""
        limit_pattern = r'\bLIMIT\s+\d+'
        sql = re.sub(limit_pattern, f"LIMIT {max_limit}", sql, flags=re.IGNORECASE)
        return sql
    
    def _estimate_complexity(self, sql: str) -> Dict[str, Any]:
        """
        Estimate query complexity and execution time.
        
        Returns:
            Dictionary with complexity analysis
        """
        complexity = {
            "complexity_level": "low",
            "estimated_time": 0.1,
            "reason": ""
        }
        
        sql_upper = sql.upper()
        
        # Count JOINs
        join_count = sql_upper.count(" JOIN ")
        
        # Count subqueries
        subquery_count = sql_upper.count("SELECT") - 1
        
        # Check for aggregations
        has_group_by = "GROUP BY" in sql_upper
        has_order_by = "ORDER BY" in sql_upper
        has_distinct = "DISTINCT" in sql_upper
        
        # Calculate complexity score
        score = 0
        score += join_count * 2
        score += subquery_count * 3
        score += 1 if has_group_by else 0
        score += 1 if has_order_by else 0
        score += 1 if has_distinct else 0
        
        # Estimate time based on complexity
        if score == 0:
            complexity["complexity_level"] = "low"
            complexity["estimated_time"] = 0.1
        elif score <= 3:
            complexity["complexity_level"] = "low"
            complexity["estimated_time"] = 0.5
        elif score <= 6:
            complexity["complexity_level"] = "medium"
            complexity["estimated_time"] = 2.0
            complexity["reason"] = f"{join_count} JOINs, {subquery_count} subqueries"
        else:
            complexity["complexity_level"] = "high"
            complexity["estimated_time"] = 5.0
            complexity["reason"] = f"{join_count} JOINs, {subquery_count} subqueries, complex aggregations"
        
        return complexity
    
    def _count_subquery_depth(self, sql: str) -> int:
        """Count the maximum depth of nested subqueries."""
        depth = 0
        max_depth = 0
        
        for char in sql:
            if char == "(":
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == ")":
                depth -= 1
        
        return max_depth


# Global sandbox instance with default settings
sql_sandbox = SQLSandbox(
    max_rows=1000,
    max_timeout_seconds=30,
    allow_write=False,
    allow_ddl=False
)


if __name__ == "__main__":
    """Test SQL Sandbox"""
    print("=== SQL Sandbox Test ===\n")
    
    test_cases = [
        # Safe queries
        ("SELECT * FROM Customer;", "Safe SELECT without LIMIT"),
        ("SELECT * FROM Customer LIMIT 10;", "Safe SELECT with LIMIT"),
        
        # Queries needing modification
        ("SELECT * FROM Customer LIMIT 5000;", "LIMIT exceeds maximum"),
        
        # Dangerous queries
        ("DROP TABLE Customer;", "DDL operation"),
        ("DELETE FROM Customer WHERE CustomerId = 1;", "Write operation"),
        ("SELECT * FROM Customer; DROP TABLE Album;", "SQL injection attempt"),
        
        # Complex queries
        (
            """
            SELECT c.FirstName, c.LastName, SUM(i.Total) as Total
            FROM Customer c
            JOIN Invoice i ON c.CustomerId = i.CustomerId
            JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
            GROUP BY c.CustomerId
            ORDER BY Total DESC
            """,
            "Complex query with multiple JOINs"
        )
    ]
    
    for i, (sql, description) in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {description}")
        print(f"{'='*60}")
        print(f"SQL: {sql.strip()[:100]}...")
        
        result = sql_sandbox.check_sql(sql)
        
        print(f"\nResult:")
        print(f"  Allowed: {'✓' if result['allowed'] else '✗'}")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Estimated Time: {result['estimated_timeout']:.2f}s")
        
        if result['issues']:
            print(f"\n  Issues:")
            for issue in result['issues']:
                print(f"    ✗ {issue}")
        
        if result['warnings']:
            print(f"\n  Warnings:")
            for warning in result['warnings']:
                print(f"    ⚠️  {warning}")
        
        if result['modifications']:
            print(f"\n  Modifications: {result['modifications']}")
            if result['safe_sql'] != result['original_sql']:
                print(f"  Safe SQL: {result['safe_sql'][:100]}...")
    
    print(f"\n{'='*60}")
    print("Test Complete!")
    print(f"{'='*60}")
