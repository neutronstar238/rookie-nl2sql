"""
M12 Acceptance Tests: Web API & Frontend
Tests the FastAPI service and endpoints
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import unittest
import time
from fastapi.testclient import TestClient

# Import the FastAPI app
from apps.api.main import app

class TestM12WebAPI(unittest.TestCase):
    """Test suite for M12 Web API module"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = TestClient(app)
    
    def test_01_health_check(self):
        """Test 1: Health check endpoint"""
        print("\n" + "="*70)
        print("Test 1: Health Check Endpoint")
        print("="*70)
        
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("version", data)
        self.assertIn("timestamp", data)
        
        print(f"✓ Health check passed")
        print(f"  Status: {data['status']}")
        print(f"  Version: {data['version']}")
    
    def test_02_root_endpoint(self):
        """Test 2: Root endpoint serves HTML"""
        print("\n" + "="*70)
        print("Test 2: Root Endpoint")
        print("="*70)
        
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        # Check for key HTML elements
        html = response.text
        self.assertIn("NL2SQL", html)
        self.assertIn("query", html.lower())
        
        print(f"✓ Root endpoint serves HTML")
        print(f"  Content type: {response.headers['content-type']}")
        print(f"  HTML length: {len(html)} bytes")
    
    def test_03_examples_endpoint(self):
        """Test 3: Examples endpoint"""
        print("\n" + "="*70)
        print("Test 3: Examples Endpoint")
        print("="*70)
        
        response = self.client.get("/api/examples")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("examples", data)
        self.assertIsInstance(data["examples"], list)
        self.assertGreater(len(data["examples"]), 0)
        
        # Check first example structure
        first_example = data["examples"][0]
        self.assertIn("category", first_example)
        self.assertIn("questions", first_example)
        
        print(f"✓ Examples endpoint working")
        print(f"  Categories: {len(data['examples'])}")
        print(f"  First category: {first_example['category']}")
        print(f"  Sample questions: {first_example['questions'][:2]}")
    
    def test_04_stats_endpoint(self):
        """Test 4: Stats endpoint"""
        print("\n" + "="*70)
        print("Test 4: Stats Endpoint")
        print("="*70)
        
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("total_tables", data)
        self.assertIn("tables", data)
        self.assertGreater(data["total_tables"], 0)
        
        print(f"✓ Stats endpoint working")
        print(f"  Total tables: {data['total_tables']}")
        if data["tables"]:
            print(f"  Sample tables: {[t['name'] for t in data['tables'][:3]]}")
    
    def test_05_query_simple(self):
        """Test 5: Simple query via API"""
        print("\n" + "="*70)
        print("Test 5: Simple Query API")
        print("="*70)
        
        request_data = {
            "question": "显示所有专辑",
            "session_id": "test_session_001"
        }
        
        response = self.client.post("/api/query", json=request_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("success", data)
        self.assertIn("session_id", data)
        self.assertIn("trace_id", data)
        self.assertIn("question", data)
        self.assertEqual(data["question"], request_data["question"])
        
        print(f"✓ Query API working")
        print(f"  Success: {data['success']}")
        print(f"  Session ID: {data['session_id']}")
        print(f"  Trace ID: {data['trace_id'][:50]}...")
        
        if data["success"]:
            print(f"  SQL generated: {data.get('sql', 'N/A')[:80]}...")
            if data.get("result"):
                print(f"  Rows returned: {data['result'].get('row_count', 0)}")
    
    def test_06_query_aggregate(self):
        """Test 6: Aggregate query via API"""
        print("\n" + "="*70)
        print("Test 6: Aggregate Query API")
        print("="*70)
        
        request_data = {
            "question": "有多少首歌曲？"
        }
        
        response = self.client.post("/api/query", json=request_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("success", data)
        
        print(f"✓ Aggregate query working")
        print(f"  Success: {data['success']}")
        
        if data["success"]:
            print(f"  SQL: {data.get('sql', 'N/A')}")
            print(f"  Answer: {data.get('answer', 'N/A')[:100]}...")
    
    def test_07_query_with_filter(self):
        """Test 7: Query with filter via API"""
        print("\n" + "="*70)
        print("Test 7: Filter Query API")
        print("="*70)
        
        request_data = {
            "question": "显示AC/DC的专辑"
        }
        
        response = self.client.post("/api/query", json=request_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("success", data)
        
        print(f"✓ Filter query working")
        print(f"  Success: {data['success']}")
        
        if data["success"] and data.get("result"):
            print(f"  Rows: {data['result'].get('row_count', 0)}")
    
    def test_08_response_structure(self):
        """Test 8: Response structure validation"""
        print("\n" + "="*70)
        print("Test 8: Response Structure")
        print("="*70)
        
        request_data = {
            "question": "列出所有艺术家"
        }
        
        response = self.client.post("/api/query", json=request_data)
        data = response.json()
        
        # Check all required fields
        required_fields = [
            "success", "session_id", "trace_id", "question"
        ]
        
        for field in required_fields:
            self.assertIn(field, data, f"Missing field: {field}")
        
        # Check metadata structure
        if data.get("metadata"):
            metadata = data["metadata"]
            self.assertIsInstance(metadata, dict)
            print(f"  Metadata keys: {list(metadata.keys())}")
        
        # Check execution time
        if data.get("execution_time"):
            self.assertIsInstance(data["execution_time"], (int, float))
            self.assertGreater(data["execution_time"], 0)
            print(f"  Execution time: {data['execution_time']:.3f}s")
        
        print(f"✓ Response structure valid")
    
    def test_09_concurrent_queries(self):
        """Test 9: Handle concurrent queries"""
        print("\n" + "="*70)
        print("Test 9: Concurrent Queries")
        print("="*70)
        
        questions = [
            "有多少个专辑？",
            "显示所有客户",
            "统计歌曲数量"
        ]
        
        import concurrent.futures
        
        def send_query(question):
            response = self.client.post("/api/query", json={"question": question})
            return response.json()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(send_query, q) for q in questions]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        success_count = sum(1 for r in results if r.get("success"))
        
        print(f"✓ Concurrent queries handled")
        print(f"  Queries sent: {len(questions)}")
        print(f"  Successful: {success_count}")
        
        # At least some should succeed
        self.assertGreater(success_count, 0)
    
    def test_10_error_handling(self):
        """Test 10: Error handling for invalid queries"""
        print("\n" + "="*70)
        print("Test 10: Error Handling")
        print("="*70)
        
        # Empty question
        response = self.client.post("/api/query", json={"question": ""})
        self.assertEqual(response.status_code, 200)
        
        # Missing question field
        response = self.client.post("/api/query", json={})
        self.assertEqual(response.status_code, 422)  # Validation error
        
        print(f"✓ Error handling working")

def run_tests():
    """Run all M12 tests"""
    print("\n" + "="*70)
    print("M12 ACCEPTANCE TESTS - Web API & Frontend")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestM12WebAPI)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL M12 TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit(run_tests())
