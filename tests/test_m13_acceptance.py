"""
M13 Deployment & Configuration Acceptance Tests
Tests the complete deployment, configuration, and system integration
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import time
import json
import subprocess
import requests
from typing import Dict, Any, List
import sqlite3

# Test configuration
TEST_TIMEOUT = 120  # seconds


class TestM13Deployment:
    """M13: Complete deployment and configuration tests"""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.start_time = time.time()
        
    def log_result(self, test_name: str, passed: bool, message: str = "", details: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        if passed:
            self.passed += 1
            print(f"  ✓ {test_name}")
            if message:
                print(f"    {message}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}")
            print(f"    ERROR: {message}")
            if details:
                print(f"    Details: {details}")
    
    def test_1_file_structure(self):
        """Test 1: Verify deployment file structure"""
        print("\n[Test 1] File Structure Verification")
        
        required_files = [
            "Dockerfile",
            "docker-compose.yml",
            ".env.example",
            ".dockerignore",
            "configs/prod.yaml",
            "configs/dev.yaml",
            "scripts/deploy.sh",
            "scripts/local_start.sh",
            "scripts/setup_db.py",
            "requirements.txt",
            "README.md",
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            exists = full_path.exists()
            self.log_result(
                f"File exists: {file_path}",
                exists,
                f"Found at {full_path}" if exists else f"Missing: {full_path}"
            )
    
    def test_2_configuration_files(self):
        """Test 2: Validate configuration files"""
        print("\n[Test 2] Configuration Files Validation")
        
        # Test .env.example
        env_example = project_root / ".env.example"
        if env_example.exists():
            content = env_example.read_text()
            required_vars = [
                "LLM_PROVIDER",
                "DEEPSEEK_API_KEY",
                "DB_TYPE",
                "DB_PATH",
                "LOG_LEVEL"
            ]
            
            for var in required_vars:
                has_var = var in content
                self.log_result(
                    f".env.example contains {var}",
                    has_var,
                    "Present" if has_var else "Missing"
                )
        
        # Test prod.yaml
        prod_yaml = project_root / "configs" / "prod.yaml"
        if prod_yaml.exists():
            content = prod_yaml.read_text()
            self.log_result(
                "prod.yaml is valid",
                "environment: \"production\"" in content,
                "Production config detected"
            )
    
    def test_3_docker_files(self):
        """Test 3: Validate Docker configuration"""
        print("\n[Test 3] Docker Configuration Validation")
        
        # Test Dockerfile
        dockerfile = project_root / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text()
            checks = {
                "Base image": "FROM python:" in content,
                "Working directory": "WORKDIR" in content,
                "Dependencies": "requirements.txt" in content,
                "Port exposure": "EXPOSE 8000" in content,
                "Health check": "HEALTHCHECK" in content,
                "CMD defined": "CMD" in content
            }
            
            for check_name, result in checks.items():
                self.log_result(
                    f"Dockerfile - {check_name}",
                    result,
                    "OK" if result else "Missing"
                )
        
        # Test docker-compose.yml
        compose_file = project_root / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            checks = {
                "Version defined": "version:" in content,
                "Services defined": "services:" in content,
                "API service": "nl2sql-api:" in content,
                "Port mapping": "8000:8000" in content,
                "Environment vars": "environment:" in content,
                "Health check": "healthcheck:" in content
            }
            
            for check_name, result in checks.items():
                self.log_result(
                    f"docker-compose.yml - {check_name}",
                    result,
                    "OK" if result else "Missing"
                )
    
    def test_4_deployment_scripts(self):
        """Test 4: Validate deployment scripts"""
        print("\n[Test 4] Deployment Scripts Validation")
        
        scripts = ["deploy.sh", "local_start.sh"]
        
        for script_name in scripts:
            script_path = project_root / "scripts" / script_name
            
            if script_path.exists():
                # Check if executable
                is_executable = os.access(script_path, os.X_OK)
                self.log_result(
                    f"{script_name} is executable",
                    is_executable,
                    "Executable" if is_executable else "Not executable"
                )
                
                # Check content
                content = script_path.read_text()
                has_shebang = content.startswith("#!/bin/bash")
                self.log_result(
                    f"{script_name} has shebang",
                    has_shebang,
                    "Valid bash script" if has_shebang else "Missing shebang"
                )
    
    def test_5_environment_variables(self):
        """Test 5: Environment variables configuration"""
        print("\n[Test 5] Environment Variables")
        
        env_file = project_root / ".env"
        
        if env_file.exists():
            # Load .env file
            env_vars = {}
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value
            
            # Check critical variables
            checks = {
                "LLM_PROVIDER": "LLM_PROVIDER" in env_vars,
                "API_KEY configured": any(
                    "API_KEY" in k and env_vars.get(k) and "your-" not in env_vars.get(k)
                    for k in env_vars
                ),
                "DB_PATH": "DB_PATH" in env_vars,
                "LOG_LEVEL": "LOG_LEVEL" in env_vars
            }
            
            for check_name, result in checks.items():
                self.log_result(
                    f"Environment: {check_name}",
                    result,
                    "Configured" if result else "Missing or placeholder"
                )
        else:
            self.log_result(
                "Environment file exists",
                False,
                ".env file not found (use .env.example as template)"
            )
    
    def test_6_database_setup(self):
        """Test 6: Database configuration and accessibility"""
        print("\n[Test 6] Database Setup")
        
        db_path = project_root / "data" / "chinook.db"
        
        # Check if database exists
        db_exists = db_path.exists()
        self.log_result(
            "Database file exists",
            db_exists,
            f"Found at {db_path}" if db_exists else "Run scripts/setup_db.py"
        )
        
        if db_exists:
            try:
                # Test database connection
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Check tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                self.log_result(
                    "Database has tables",
                    len(tables) > 0,
                    f"Found {len(tables)} tables"
                )
                
                # Check specific tables
                expected_tables = ["Album", "Artist", "Customer", "Track", "Invoice"]
                for table in expected_tables:
                    has_table = table in tables
                    self.log_result(
                        f"Table exists: {table}",
                        has_table,
                        "OK" if has_table else "Missing"
                    )
                
                # Check data
                cursor.execute("SELECT COUNT(*) FROM Album")
                album_count = cursor.fetchone()[0]
                self.log_result(
                    "Database has data",
                    album_count > 0,
                    f"Album table has {album_count} records"
                )
                
                conn.close()
                
            except Exception as e:
                self.log_result(
                    "Database connection test",
                    False,
                    f"Failed: {str(e)}"
                )
    
    def test_7_dependencies(self):
        """Test 7: Python dependencies"""
        print("\n[Test 7] Python Dependencies")
        
        required_packages = [
            "langgraph",
            "langchain",
            "langchain_openai",
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.log_result(
                    f"Package installed: {package}",
                    True,
                    "OK"
                )
            except ImportError:
                self.log_result(
                    f"Package installed: {package}",
                    False,
                    "Not installed - run: pip install -r requirements.txt"
                )
    
    def test_8_api_server_startup(self):
        """Test 8: API server can start (if not already running)"""
        print("\n[Test 8] API Server Startup Test")
        
        # Check if server is already running
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                self.log_result(
                    "API server is accessible",
                    True,
                    "Server already running on port 8000"
                )
                self.test_9_api_endpoints()
                return
        except:
            pass
        
        # Try to import and validate API app
        try:
            from apps.api.main import app
            self.log_result(
                "API app can be imported",
                True,
                "FastAPI app loaded successfully"
            )
            
            # Check routes
            routes = [route.path for route in app.routes]
            expected_routes = ["/health", "/api/query", "/api/examples"]
            
            for route in expected_routes:
                has_route = route in routes
                self.log_result(
                    f"API route exists: {route}",
                    has_route,
                    "Registered" if has_route else "Missing"
                )
                
        except Exception as e:
            self.log_result(
                "API app import test",
                False,
                f"Failed: {str(e)}"
            )
    
    def test_9_api_endpoints(self):
        """Test 9: API endpoints functionality"""
        print("\n[Test 9] API Endpoints")
        
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            self.log_result(
                "Health endpoint",
                response.status_code == 200,
                f"Status: {response.status_code}",
                response.json() if response.status_code == 200 else None
            )
        except Exception as e:
            self.log_result(
                "Health endpoint",
                False,
                f"Failed: {str(e)}"
            )
        
        # Test examples endpoint
        try:
            response = requests.get(f"{base_url}/api/examples", timeout=5)
            self.log_result(
                "Examples endpoint",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.log_result(
                "Examples endpoint",
                False,
                f"Failed: {str(e)}"
            )
    
    def test_10_system_integration(self):
        """Test 10: Full system integration test"""
        print("\n[Test 10] System Integration")
        
        # Check if all components can work together
        try:
            # Import core modules
            from graphs.base_graph import build_graph
            from tools.db import db_client
            from tools.llm_client import LLMClient
            
            self.log_result(
                "Core modules import",
                True,
                "All core modules loaded successfully"
            )
            
            # Test database client
            try:
                result = db_client.test_connection()
                self.log_result(
                    "Database client connection",
                    result,
                    "Connected" if result else "Failed"
                )
            except Exception as e:
                self.log_result(
                    "Database client connection",
                    False,
                    f"Error: {str(e)}"
                )
            
            # Test LLM client (just initialization, no API call)
            try:
                from tools.llm_client import LLMClient
                llm_client = LLMClient()
                self.log_result(
                    "LLM client initialization",
                    llm_client is not None,
                    "LLM client created successfully"
                )
            except Exception as e:
                self.log_result(
                    "LLM client initialization",
                    False,
                    f"Error: {str(e)}"
                )
            
            # Test graph building
            try:
                graph = build_graph()
                self.log_result(
                    "Graph building",
                    graph is not None,
                    "LangGraph compiled successfully"
                )
            except Exception as e:
                self.log_result(
                    "Graph building",
                    False,
                    f"Error: {str(e)}"
                )
                
        except Exception as e:
            self.log_result(
                "System integration",
                False,
                f"Failed: {str(e)}"
            )
    
    def test_11_end_to_end(self):
        """Test 11: End-to-end query test"""
        print("\n[Test 11] End-to-End Query Test")
        
        # Check if API is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code != 200:
                self.log_result(
                    "End-to-end test",
                    False,
                    "API server not running. Start with: bash scripts/local_start.sh"
                )
                return
        except:
            self.log_result(
                "End-to-end test",
                False,
                "API server not running. Start with: bash scripts/local_start.sh"
            )
            return
        
        # Test simple query
        test_query = "How many albums are there?"
        
        try:
            response = requests.post(
                "http://localhost:8000/api/query",
                json={"question": test_query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                self.log_result(
                    "E2E: Query accepted",
                    True,
                    f"Response received in {result.get('execution_time', 0):.2f}s"
                )
                
                self.log_result(
                    "E2E: SQL generated",
                    result.get("sql") is not None,
                    f"SQL: {result.get('sql', 'N/A')[:100]}"
                )
                
                self.log_result(
                    "E2E: Query successful",
                    result.get("success", False),
                    f"Success: {result.get('success')}"
                )
                
                if result.get("result"):
                    exec_result = result["result"]
                    self.log_result(
                        "E2E: Results returned",
                        exec_result.get("ok", False),
                        f"Rows: {exec_result.get('row_count', 0)}"
                    )
            else:
                self.log_result(
                    "E2E: Query execution",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_result(
                "End-to-end test",
                False,
                f"Error: {str(e)}"
            )
    
    def test_12_documentation(self):
        """Test 12: Documentation completeness"""
        print("\n[Test 12] Documentation")
        
        docs = [
            ("README.md", ["快速开始", "配置", "API", "部署", "Docker"]),  # Main unified README
        ]
        
        for doc_file, keywords in docs:
            doc_path = project_root / doc_file
            
            if doc_path.exists():
                content = doc_path.read_text().lower()
                
                for keyword in keywords:
                    has_keyword = keyword.lower() in content
                    self.log_result(
                        f"{doc_file} mentions '{keyword}'",
                        has_keyword,
                        "Found" if has_keyword else "Missing"
                    )
            else:
                self.log_result(
                    f"Documentation exists: {doc_file}",
                    False,
                    "File not found"
                )
    
    def run_all_tests(self):
        """Run all acceptance tests"""
        print("\n" + "=" * 60)
        print("M13 DEPLOYMENT & CONFIGURATION ACCEPTANCE TESTS")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_1_file_structure,
            self.test_2_configuration_files,
            self.test_3_docker_files,
            self.test_4_deployment_scripts,
            self.test_5_environment_variables,
            self.test_6_database_setup,
            self.test_7_dependencies,
            self.test_8_api_server_startup,
            self.test_10_system_integration,
            self.test_11_end_to_end,
            self.test_12_documentation,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"\n  ✗ Test failed with exception: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        duration = time.time() - self.start_time
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests:  {total}")
        print(f"Passed:       {self.passed} ({pass_rate:.1f}%)")
        print(f"Failed:       {self.failed}")
        print(f"Duration:     {duration:.2f}s")
        print("=" * 60)
        
        if self.failed == 0:
            print("✓ ALL TESTS PASSED!")
            print("\nDeployment Status: READY FOR PRODUCTION")
        else:
            print(f"✗ {self.failed} TEST(S) FAILED")
            print("\nPlease fix the failing tests before deployment.")
        
        print("\n" + "=" * 60)
        
        # Save results to file
        results_file = project_root / "logs" / "m13_test_results.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": self.passed,
                    "failed": self.failed,
                    "pass_rate": pass_rate,
                    "duration": duration,
                    "timestamp": time.time()
                },
                "tests": self.test_results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")


if __name__ == "__main__":
    tester = TestM13Deployment()
    tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if tester.failed == 0 else 1)
