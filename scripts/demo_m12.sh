#!/bin/bash
# M12 Demo Script - Quick demonstration of Web API

echo "========================================"
echo "M12 - Web API & Frontend Demo"
echo "========================================"
echo ""

# Check if server is running
echo "1. Checking if API server is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ API server is running"
else
    echo "   ❌ API server is not running"
    echo ""
    echo "Please start the server first:"
    echo "  ./scripts/start_api.sh"
    echo ""
    echo "Or run in background:"
    echo "  cd apps/api && nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &"
    exit 1
fi

echo ""
echo "2. Testing API endpoints..."
echo ""

# Health check
echo "   Testing /health endpoint:"
curl -s http://localhost:8000/health | python3 -m json.tool | head -5
echo ""

# Examples
echo "   Testing /api/examples endpoint:"
curl -s http://localhost:8000/api/examples | python3 -m json.tool | head -10
echo ""

# Stats
echo "   Testing /api/stats endpoint:"
curl -s http://localhost:8000/api/stats | python3 -m json.tool | head -10
echo ""

# Query
echo "3. Testing query API with sample question..."
echo "   Question: 显示所有专辑"
echo ""

curl -s -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "显示所有专辑"}' | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Success: {data.get('success')}\")
print(f\"   SQL: {data.get('sql', 'N/A')[:60]}...\")
print(f\"   Rows: {data.get('result', {}).get('row_count', 0)}\")
print(f\"   Time: {data.get('execution_time', 0):.2f}s\")
"

echo ""
echo "========================================"
echo "✓ Demo completed!"
echo ""
echo "Web Interface: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "========================================"
