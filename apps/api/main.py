"""
FastAPI Web Service for NL2SQL System
M12: Web API with interactive frontend
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import traceback

from graphs.base_graph import build_graph
from graphs.state import NL2SQLState

# Create FastAPI app
app = FastAPI(
    title="NL2SQL API",
    description="Natural Language to SQL Query System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
from pathlib import Path
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    session_id: str
    trace_id: str
    question: str
    sql: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    answer: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# Initialize graph
nl2sql_graph = None

def get_graph():
    """Lazy load the NL2SQL graph"""
    global nl2sql_graph
    if nl2sql_graph is None:
        nl2sql_graph = build_graph()
    return nl2sql_graph

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    print("Starting NL2SQL API server...")
    # Pre-load the graph
    get_graph()
    print("NL2SQL graph loaded successfully")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend HTML"""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
        <html>
            <body>
                <h1>NL2SQL API</h1>
                <p>Frontend not found. Please ensure static/index.html exists.</p>
                <p>API Documentation: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Execute a natural language query
    
    Args:
        request: QueryRequest with question and optional session_id
        
    Returns:
        QueryResponse with SQL, results, and answer
    """
    start_time = datetime.now()
    
    # Generate IDs
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
    trace_id = f"trace_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}"
    
    print(f"[{trace_id}] Received query: {request.question}")
    
    try:
        # Create initial state
        initial_state: NL2SQLState = {
            "question": request.question,
            "session_id": session_id,
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            
            # Initialize all required fields
            "intent": None,
            "schema_context": None,
            "rag_context": None,
            "candidate_sql": None,
            "validation_result": None,
            "retry_count": 0,
            "execution_result": None,
            "answer": None,
            "error": None,
            
            # Metadata
            "sql_generated_at": None,
            "executed_at": None,
            "answer_generated_at": None,
            "node_timings": {},
            "total_llm_tokens": 0
        }
        
        # Run the graph
        graph = get_graph()
        result = graph.invoke(initial_state)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Extract results
        success = result.get("execution_result", {}).get("ok", False) if result.get("execution_result") else False
        
        response = QueryResponse(
            success=success,
            session_id=session_id,
            trace_id=trace_id,
            question=request.question,
            sql=result.get("candidate_sql"),
            result=result.get("execution_result"),
            answer=result.get("answer"),
            error=result.get("error"),
            execution_time=execution_time,
            metadata={
                "intent": result.get("intent"),
                "retry_count": result.get("retry_count", 0),
                "node_timings": result.get("node_timings", {}),
                "total_llm_tokens": result.get("total_llm_tokens", 0)
            }
        )
        
        print(f"[{trace_id}] Query completed in {execution_time:.2f}s - Success: {success}")
        
        return response
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        print(f"[{trace_id}] Query failed: {error_msg}")
        
        return QueryResponse(
            success=False,
            session_id=session_id,
            trace_id=trace_id,
            question=request.question,
            error=error_msg,
            execution_time=execution_time
        )

@app.get("/api/examples")
async def get_examples():
    """Get example queries"""
    examples = [
        {
            "category": "简单查询",
            "questions": [
                "显示所有专辑",
                "查询所有艺术家",
                "列出所有客户",
            ]
        },
        {
            "category": "聚合统计",
            "questions": [
                "有多少首歌曲？",
                "有多少个专辑？",
                "统计客户总数",
            ]
        },
        {
            "category": "排序查询",
            "questions": [
                "显示前5个最长的歌曲",
                "查询价格最高的10首歌",
                "最新的5个订单",
            ]
        },
        {
            "category": "过滤查询",
            "questions": [
                "显示AC/DC的专辑",
                "查找摇滚类型的歌曲",
                "2010年的订单",
            ]
        },
        {
            "category": "联表查询",
            "questions": [
                "显示所有专辑及其艺术家名称",
                "查询客户的订单总额",
                "每个风格有多少首歌？",
            ]
        },
    ]
    return {"examples": examples}

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    from tools.db import db_client
    
    try:
        # Get table counts
        tables = db_client.get_table_names()
        stats = {
            "total_tables": len(tables),
            "tables": []
        }
        
        for table in tables[:5]:  # Limit to first 5 tables
            try:
                result = db_client.query(f"SELECT COUNT(*) as count FROM {table}")
                if result.get("ok") and result.get("rows"):
                    count = result["rows"][0]["count"]
                    stats["tables"].append({"name": table, "row_count": count})
            except:
                pass
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
