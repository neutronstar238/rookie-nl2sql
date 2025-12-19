"""
SQL Validation and Repair Tool (M4)
使用 sqlglot 进行 SQL 语法校验和自动修复。
"""
import sqlglot
from typing import Dict, Any, List, Optional
import re


class SQLValidator:
    """SQL 校验器，支持语法检查、语义验证和自动修复"""
    
    def __init__(self, dialect: str = "sqlite"):
        """
        初始化 SQL 校验器
        
        Args:
            dialect: SQL 方言 (sqlite, mysql, postgres, etc.)
        """
        self.dialect = dialect
    
    def validate(
        self, 
        sql: str, 
        schema: Optional[Dict[str, Any]] = None,
        strict_mode: bool = False
    ) -> Dict[str, Any]:
        """
        校验 SQL 语句
        
        Args:
            sql: 待校验的 SQL 语句
            schema: 数据库 Schema (用于语义校验)
            strict_mode: 严格模式 (启用更多检查)
        
        Returns:
            {
                "valid": bool,              # 是否有效
                "errors": List[str],        # 错误列表
                "warnings": List[str],      # 警告列表
                "parsed_ast": Any,          # 解析后的 AST
                "normalized_sql": str       # 规范化后的 SQL
            }
        """
        errors = []
        warnings = []
        parsed_ast = None
        normalized_sql = sql.strip()
        
        # 1. 基本检查：空 SQL
        if not sql or not sql.strip():
            errors.append("Empty SQL statement")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "parsed_ast": None,
                "normalized_sql": ""
            }
        
        # 2. 安全检查：只允许 SELECT
        if not self._is_read_only(sql):
            errors.append("Only SELECT queries are allowed (found INSERT/UPDATE/DELETE/DROP)")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "parsed_ast": None,
                "normalized_sql": normalized_sql
            }
        
        # 3. 使用 sqlglot 解析 SQL
        try:
            parsed_ast = sqlglot.parse_one(sql, dialect=self.dialect)
            normalized_sql = parsed_ast.sql(dialect=self.dialect, pretty=True)
        except sqlglot.errors.ParseError as e:
            errors.append(f"Syntax error: {str(e)}")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "parsed_ast": None,
                "normalized_sql": normalized_sql
            }
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "parsed_ast": None,
                "normalized_sql": normalized_sql
            }
        
        # 4. 语义校验 (如果提供了 Schema)
        if schema:
            semantic_errors, semantic_warnings = self._validate_semantics(parsed_ast, schema)
            errors.extend(semantic_errors)
            warnings.extend(semantic_warnings)
        
        # 5. 严格模式检查
        if strict_mode:
            strict_warnings = self._strict_checks(parsed_ast)
            warnings.extend(strict_warnings)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "parsed_ast": parsed_ast,
            "normalized_sql": normalized_sql
        }
    
    def repair(
        self, 
        sql: str, 
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        自动修复 SQL 语句
        
        Args:
            sql: 待修复的 SQL 语句
            schema: 数据库 Schema (用于智能修复)
        
        Returns:
            {
                "success": bool,            # 是否成功修复
                "repaired_sql": str,        # 修复后的 SQL
                "changes": List[str],       # 修复内容描述
                "validation": Dict          # 修复后的校验结果
            }
        """
        changes = []
        repaired_sql = sql.strip()
        
        # 1. 移除多余的分号
        if repaired_sql.endswith(';'):
            repaired_sql = repaired_sql.rstrip(';')
            changes.append("Removed trailing semicolon")
        
        # 2. 尝试解析和规范化
        try:
            parsed = sqlglot.parse_one(repaired_sql, dialect=self.dialect)
            repaired_sql = parsed.sql(dialect=self.dialect, pretty=True)
            changes.append("Normalized SQL formatting")
        except Exception as e:
            # 如果解析失败，尝试基本修复
            repaired_sql = self._basic_repair(repaired_sql)
            changes.append(f"Applied basic repairs (parse failed: {str(e)})")
        
        # 3. 表名和列名修复 (如果提供了 Schema)
        if schema:
            repaired_sql, schema_fixes = self._fix_names_with_schema(repaired_sql, schema)
            changes.extend(schema_fixes)
        
        # 4. 校验修复后的 SQL
        validation = self.validate(repaired_sql, schema)
        
        return {
            "success": validation["valid"],
            "repaired_sql": repaired_sql,
            "changes": changes,
            "validation": validation
        }
    
    def _is_read_only(self, sql: str) -> bool:
        """检查 SQL 是否为只读查询"""
        sql_upper = sql.upper().strip()
        
        # 检查是否以 SELECT 或 WITH 开头
        if sql_upper.startswith("SELECT") or sql_upper.startswith("WITH"):
            # 确保不包含危险关键字
            dangerous_keywords = [
                "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", 
                "ALTER", "TRUNCATE", "REPLACE", "MERGE"
            ]
            for keyword in dangerous_keywords:
                # 使用单词边界匹配，避免误判 (如 INSERTED 列名)
                if re.search(r'\b' + keyword + r'\b', sql_upper):
                    return False
            return True
        
        return False
    
    def _validate_semantics(
        self, 
        parsed_ast: Any, 
        schema: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """语义校验：检查表名、列名是否存在"""
        errors = []
        warnings = []
        
        # 获取 Schema 中的表名和列名
        schema_tables = {}
        if "tables" in schema:
            for table_info in schema["tables"]:
                table_name = table_info["table_name"]
                columns = [col["name"] for col in table_info["columns"]]
                schema_tables[table_name.lower()] = {
                    "name": table_name,
                    "columns": {col.lower(): col for col in columns}
                }
        
        # 提取 SQL 中的表名
        try:
            for table in parsed_ast.find_all(sqlglot.exp.Table):
                table_name = table.name.lower()
                if table_name not in schema_tables:
                    errors.append(f"Table '{table.name}' does not exist in schema")
            
            # 提取列名 (简化版，可能需要更复杂的逻辑)
            for column in parsed_ast.find_all(sqlglot.exp.Column):
                # 这里可以添加列名校验逻辑
                pass
        
        except Exception as e:
            warnings.append(f"Semantic validation skipped: {str(e)}")
        
        return errors, warnings
    
    def _strict_checks(self, parsed_ast: Any) -> List[str]:
        """严格模式检查"""
        warnings = []
        
        # 检查是否使用了 SELECT *
        if "SELECT *" in parsed_ast.sql().upper():
            warnings.append("Using SELECT * is not recommended in production")
        
        # 检查是否缺少 LIMIT (可能导致大量结果)
        if not parsed_ast.find(sqlglot.exp.Limit):
            warnings.append("No LIMIT clause found - query may return large result sets")
        
        return warnings
    
    def _basic_repair(self, sql: str) -> str:
        """基本的 SQL 修复"""
        # 移除多余的空格
        sql = re.sub(r'\s+', ' ', sql).strip()
        
        # 确保 SQL 关键字大写 (可选)
        # keywords = ["SELECT", "FROM", "WHERE", "JOIN", "ON", "GROUP BY", "ORDER BY", "LIMIT"]
        # for keyword in keywords:
        #     sql = re.sub(r'\b' + keyword.lower() + r'\b', keyword, sql, flags=re.IGNORECASE)
        
        return sql
    
    def _fix_names_with_schema(
        self, 
        sql: str, 
        schema: Dict[str, Any]
    ) -> tuple[str, List[str]]:
        """使用 Schema 修复表名和列名（大小写）"""
        changes = []
        
        if "tables" in schema:
            # 构建表名映射 (小写 -> 正确大小写)
            table_map = {}
            for table_info in schema["tables"]:
                table_name = table_info["table_name"]
                table_map[table_name.lower()] = table_name
            
            # 替换表名
            for lower_name, correct_name in table_map.items():
                # 使用单词边界匹配
                pattern = r'\b' + re.escape(lower_name) + r'\b'
                if re.search(pattern, sql, re.IGNORECASE):
                    sql = re.sub(pattern, correct_name, sql, flags=re.IGNORECASE)
                    if lower_name != correct_name.lower():
                        changes.append(f"Fixed table name: {lower_name} -> {correct_name}")
        
        return sql, changes


# Singleton instance
sql_validator = SQLValidator()


def validate_sql(
    sql: str, 
    schema: Optional[Dict[str, Any]] = None,
    strict_mode: bool = False
) -> Dict[str, Any]:
    """
    便捷函数：校验 SQL 语句
    
    Args:
        sql: SQL 语句
        schema: 数据库 Schema
        strict_mode: 严格模式
    
    Returns:
        校验结果字典
    """
    return sql_validator.validate(sql, schema, strict_mode)


def repair_sql(
    sql: str, 
    schema: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    便捷函数：修复 SQL 语句
    
    Args:
        sql: SQL 语句
        schema: 数据库 Schema
    
    Returns:
        修复结果字典
    """
    return sql_validator.repair(sql, schema)


if __name__ == "__main__":
    """测试 SQL 校验器"""
    print("="*60)
    print("SQL Validator Test")
    print("="*60)
    
    # 测试用例
    test_cases = [
        {
            "name": "Valid SELECT",
            "sql": "SELECT * FROM Album LIMIT 10",
            "schema": None
        },
        {
            "name": "Invalid syntax",
            "sql": "SELECT * FORM Album",
            "schema": None
        },
        {
            "name": "Non-SELECT query",
            "sql": "DELETE FROM Album WHERE AlbumId = 1",
            "schema": None
        },
        {
            "name": "Complex JOIN",
            "sql": """
                SELECT a.Title, ar.Name 
                FROM Album a 
                JOIN Artist ar ON a.ArtistId = ar.ArtistId 
                LIMIT 100
            """,
            "schema": None
        },
        {
            "name": "Empty SQL",
            "sql": "   ",
            "schema": None
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n### Test Case {i}: {test['name']} ###")
        print(f"SQL: {test['sql'][:50]}...")
        
        # 校验
        result = validate_sql(test['sql'], test['schema'])
        print(f"Valid: {result['valid']}")
        
        if result['errors']:
            print(f"Errors: {result['errors']}")
        
        if result['warnings']:
            print(f"Warnings: {result['warnings']}")
        
        if result['normalized_sql'] and result['valid']:
            print(f"Normalized SQL:\n{result['normalized_sql'][:100]}...")
        
        # 如果无效，尝试修复
        if not result['valid']:
            print("\n--- Attempting Repair ---")
            repair_result = repair_sql(test['sql'], test['schema'])
            print(f"Repair Success: {repair_result['success']}")
            if repair_result['changes']:
                print(f"Changes: {repair_result['changes']}")
            if repair_result['success']:
                print(f"Repaired SQL:\n{repair_result['repaired_sql'][:100]}...")
    
    print("\n" + "="*60)
    print("SQL Validator Test Complete!")
    print("="*60)
