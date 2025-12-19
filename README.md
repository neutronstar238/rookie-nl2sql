# NL2SQL LangGraph 系统

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于 LangGraph 构建的生产级自然语言转SQL（NL2SQL）智能代理系统。支持多轮对话、意图消歧、SQL自动修复、RAG检索增强、安全沙箱执行等企业级特性。

## 🌟 核心特性

### 🎯 完整的 NL2SQL 能力
- ✅ **智能SQL生成** - 基于 LLM 的自然语言到 SQL 转换
- ✅ **Schema感知** - 自动理解数据库结构，避免幻觉字段
- ✅ **SQL校验与修复** - 语法检查、自动修复错误SQL
- ✅ **安全沙箱** - 只读权限、超时控制、危险操作拦截
- ✅ **多表联结** - 支持复杂JOIN查询和Few-shot模板

### 🚀 高级功能
- ✅ **RAG检索增强** - 行业术语识别、历史SQL复用
- ✅ **多轮对话** - 意图澄清、上下文理解
- ✅ **自然语言答案** - 将查询结果转换为友好回答
- ✅ **完整可观测性** - TraceID追踪、结构化日志、性能监控
- ✅ **评测框架** - 自动化测试、性能基准、质量评估

### 🛠️ 生产就绪
- ✅ **Web API** - FastAPI RESTful 接口
- ✅ **前端界面** - 交互式查询界面
- ✅ **Docker部署** - 一键容器化部署
- ✅ **多LLM支持** - DeepSeek / 通义千问 / OpenAI
- ✅ **企业级配置** - 开发/生产环境分离

---

## 📋 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd nl2sql-langgraph

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 3. 一键部署
bash scripts/deploy.sh

# 4. 访问服务
# Web UI: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境
cp .env.example .env
# 编辑 .env，配置 LLM API Key

# 3. 下载示例数据库
python scripts/setup_db.py

# 4. 启动服务
bash scripts/local_start.sh
# 或手动启动
python -m uvicorn apps.api.main:app --reload
```

### 方式三：命令行测试

```bash
# 运行基础图测试
python graphs/base_graph.py

# 测试数据库连接
python tools/db.py

# 运行完整测试套件
python tests/test_m13_acceptance.py
```

---

## 🎬 使用示例

### API 调用

```bash
# 查询示例
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "有多少个专辑？"}'
```

**响应：**
```json
{
  "success": true,
  "sql": "SELECT COUNT(*) AS album_count FROM Album;",
  "result": {
    "ok": true,
    "rows": [{"album_count": 347}],
    "columns": ["album_count"],
    "row_count": 1
  },
  "answer": "数据库中共有 347 个专辑。",
  "execution_time": 2.35
}
```

### Python SDK

```python
from graphs.base_graph import build_graph

# 构建图
graph = build_graph()

# 执行查询
result = graph.invoke({
    "question": "显示销售额最高的前5个客户",
    "session_id": "user_123"
})

print(f"SQL: {result['candidate_sql']}")
print(f"结果: {result['execution_result']}")
print(f"答案: {result['answer']}")
```

---

## 🏗️ 系统架构

### LangGraph 工作流

```
┌─────────────┐
│ 用户问题     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 1. 意图解析     │  识别查询意图、提取关键信息
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Schema注入   │  获取数据库结构、字段映射
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. RAG检索      │  匹配历史SQL、行业术语
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 生成SQL      │  LLM生成候选SQL
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. SQL校验      │  语法检查、安全验证
└────────┬────────┘
         │
    ┌────┴────┐
    │  失败？  │
    └────┬────┘
         │ 是
         ▼
┌─────────────────┐
│ 6. SQL修复      │  LLM修复错误SQL
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 7. 执行SQL      │  沙箱环境执行
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 8. 生成答案     │  转换为自然语言
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 返回结果        │
└─────────────────┘
```

### 技术栈

- **框架**: LangGraph + LangChain
- **LLM**: DeepSeek / 通义千问 / OpenAI
- **数据库**: SQLite (演示) / PostgreSQL / MySQL
- **向量库**: FAISS
- **Web框架**: FastAPI + Uvicorn
- **部署**: Docker + Docker Compose
- **测试**: Pytest + 自定义验收测试

---

## 📁 项目结构

```
nl2sql-langgraph/
├── apps/                    # 应用层
│   └── api/                # FastAPI Web服务
│       ├── main.py         # API入口
│       └── static/         # 前端静态文件
├── graphs/                  # LangGraph核心
│   ├── base_graph.py       # 主图定义
│   ├── state.py            # 状态结构
│   └── nodes/              # 图节点实现
│       ├── parse_intent.py
│       ├── generate_sql.py
│       ├── validate_sql.py
│       ├── execute_sql.py
│       └── answer_builder.py
├── tools/                   # 工具模块
│   ├── db.py               # 数据库客户端
│   ├── llm_client.py       # LLM客户端
│   ├── sql_validator.py    # SQL校验器
│   ├── sql_sandbox.py      # 安全沙箱
│   ├── rag_retriever.py    # RAG检索器
│   ├── schema_formatter.py # Schema格式化
│   ├── logger.py           # 日志系统
│   └── ...
├── prompts/                 # 提示词模板
│   ├── nl2sql.txt          # SQL生成模板
│   ├── answer.txt          # 答案生成模板
│   └── critique.txt        # SQL修复模板
├── configs/                 # 配置文件
│   ├── config.py           # 配置加载器
│   ├── dev.yaml            # 开发配置
│   └── prod.yaml           # 生产配置
├── data/                    # 数据目录
│   ├── chinook.db          # 示例数据库
│   └── vector_store/       # 向量库
├── eval/                    # 评测模块
│   ├── test_cases.py       # 测试用例
│   ├── runner.py           # 评测运行器
│   └── benchmark.py        # 性能基准
├── tests/                   # 测试套件
│   ├── test_m0_acceptance.py
│   ├── test_m1_acceptance.py
│   └── ...
├── scripts/                 # 脚本工具
│   ├── deploy.sh           # 部署脚本
│   ├── local_start.sh      # 本地启动
│   └── setup_db.py         # 数据库初始化
├── logs/                    # 日志目录
├── Dockerfile              # Docker镜像
├── docker-compose.yml      # 容器编排
├── requirements.txt        # Python依赖
├── .env.example            # 环境变量模板
└── README.md               # 本文档
```

---

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
# ==================== LLM配置 ====================
LLM_PROVIDER=deepseek              # LLM提供商: deepseek/qwen/openai
DEEPSEEK_API_KEY=sk-xxxxx          # DeepSeek API Key
LLM_TEMPERATURE=0.0                # 生成温度
LLM_MAX_TOKENS=4000                # 最大Token数

# ==================== 数据库配置 ====================
DB_TYPE=sqlite                     # 数据库类型
DB_PATH=data/chinook.db            # SQLite路径
# DB_TYPE=postgresql               # 生产环境推荐PostgreSQL
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=nl2sql
# DB_USER=nl2sql
# DB_PASSWORD=your-password

# ==================== RAG配置 ====================
VECTOR_STORE_TYPE=faiss            # 向量库类型
VECTOR_STORE_PATH=data/vector_store
EMBEDDING_PROVIDER=local           # Embedding提供商
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# ==================== 系统配置 ====================
LOG_LEVEL=INFO                     # 日志级别
MAX_RETRIES=3                      # 重试次数
TIMEOUT=30                         # 超时时间(秒)
```

### 支持的 LLM 提供商

#### 1. DeepSeek（推荐国内用户）
```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxx
```
获取地址：https://platform.deepseek.com/

#### 2. 通义千问 Qwen
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxxxx
```
获取地址：https://dashscope.console.aliyun.com/

#### 3. OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
```

---

## 🧪 测试

### 运行完整测试

```bash
# 运行所有验收测试
python tests/test_m13_acceptance.py

# 运行特定模块测试
python tests/test_m0_acceptance.py  # 基础架构
python tests/test_m2_acceptance.py  # 数据库功能
python tests/test_m4_acceptance.py  # SQL校验
python tests/test_m6_acceptance.py  # RAG检索
python tests/test_m11_acceptance.py # 日志系统
python tests/test_m12_acceptance.py # API服务
```

### 评测系统性能

```bash
# 运行评测基准
python eval/runner.py

# 生成性能报告
python eval/benchmark.py
```

### 测试覆盖

- ✅ **69个验收测试** (100%通过率)
- ✅ **12个测试组** 覆盖所有模块
- ✅ **端到端测试** 验证完整流程
- ✅ **性能基准测试** 确保生产质量

---

## 📊 示例数据库

项目使用 **Chinook** 数据库作为演示数据：
- 🎵 **业务场景**: 音乐商店（类似iTunes）
- 📦 **11个表**: Artist, Album, Track, Customer, Invoice等
- 📈 **3500+条记录**: 真实业务数据

### 主要表关系

```
Artist (艺术家) 
  ↓ 1:N
Album (专辑)
  ↓ 1:N  
Track (歌曲) ─→ Genre (风格)
  ↓ N:M
PlaylistTrack ─→ Playlist (播放列表)
  ↓
InvoiceLine ─→ Invoice ─→ Customer (客户)
```

### 查询示例

```sql
-- 简单查询
"有多少个专辑？"
→ SELECT COUNT(*) FROM Album;

-- 聚合统计  
"每个风格有多少首歌？"
→ SELECT g.Name, COUNT(*) as TrackCount 
  FROM Track t JOIN Genre g ON t.GenreId = g.GenreId 
  GROUP BY g.Name;

-- 多表联结
"显示销售额最高的前10个客户"
→ SELECT c.FirstName, c.LastName, SUM(i.Total) as TotalSpent
  FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId
  GROUP BY c.CustomerId ORDER BY TotalSpent DESC LIMIT 10;
```

---

## 🔧 高级功能

### 1. RAG 检索增强

自动匹配历史SQL和行业术语：

```python
# 自动识别行业黑话
"统计铁粉数量" → "统计复购次数>=3的客户"

# 复用历史SQL模板
"上月销售额" → 基于历史SQL模板生成
```

### 2. 多轮对话与意图澄清

支持上下文理解和主动澄清：

```
用户: "查询销售数据"
系统: "请问您想查询哪个时间范围的销售数据？
      1) 今天  2) 本周  3) 本月  4) 自定义"
      
用户: "本月"
系统: [生成对应SQL并执行]
```

### 3. SQL 自动修复

检测并自动修复错误SQL：

```sql
-- 错误SQL（字段名错误）
SELECT AlbumName FROM Album;

-- 自动修复
SELECT Title FROM Album;
```

### 4. 安全沙箱

多层安全防护：
- ✅ 只允许SELECT查询
- ✅ 禁止DROP/DELETE/UPDATE
- ✅ 限制返回行数（最大1000行）
- ✅ 查询超时控制（30秒）
- ✅ SQL注入防护

### 5. 完整可观测性

TraceID追踪完整链路：

```json
{
  "trace_id": "trace_a1b2c3d4_1702900800",
  "session_id": "session_12345",
  "steps": [
    {"node": "parse_intent", "duration": 0.15, "status": "ok"},
    {"node": "generate_sql", "duration": 1.23, "status": "ok"},
    {"node": "validate_sql", "duration": 0.08, "status": "ok"},
    {"node": "execute_sql", "duration": 0.45, "status": "ok"}
  ],
  "total_duration": 2.35,
  "llm_tokens": 456
}
```

---

## 🚀 部署

### Docker 部署（生产推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose stop

# 删除容器
docker-compose down
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/health

# 查看系统统计
curl http://localhost:8000/api/stats
```

### 性能优化

**生产环境配置 (configs/prod.yaml)**:
- Workers: 4个进程
- 连接池: 10-20连接
- 缓存: 启用Redis
- 超时: 60秒
- 速率限制: 60次/分钟

---

## 📖 API 文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/query` | POST | 执行NL2SQL查询 |
| `/api/examples` | GET | 获取查询示例 |
| `/api/stats` | GET | 系统统计信息 |

---

## 🎯 性能指标

### 测试结果（基于Chinook数据库）

| 指标 | 结果 |
|------|------|
| **SQL生成准确率** | 85%+ |
| **执行成功率** | 95%+ |
| **平均响应时间** | 2-4秒 |
| **自动修复成功率** | 70%+ |
| **多表JOIN准确率** | 75%+ |

### 系统能力

- ✅ 支持单表查询（SELECT, WHERE, ORDER BY, LIMIT）
- ✅ 支持聚合函数（COUNT, SUM, AVG, MAX, MIN）
- ✅ 支持GROUP BY和HAVING
- ✅ 支持多表JOIN（INNER, LEFT）
- ✅ 支持子查询（部分场景）
- ✅ 支持中文自然语言
- ✅ 支持多轮对话

---

## 🛠️ 开发指南

### 添加新的图节点

```python
# graphs/nodes/custom_node.py
from graphs.state import NL2SQLState

def custom_node(state: NL2SQLState) -> NL2SQLState:
    """自定义节点处理逻辑"""
    
    # 1. 从state获取输入
    question = state["question"]
    
    # 2. 执行处理逻辑
    result = process(question)
    
    # 3. 更新state
    state["custom_field"] = result
    
    # 4. 返回更新后的state
    return state
```

### 扩展LLM提供商

```python
# tools/llm_client.py
class LLMClient:
    def __init__(self, provider: str):
        if provider == "custom":
            # 添加自定义LLM配置
            self.client = CustomLLM(...)
```

### 自定义提示词模板

编辑 `prompts/` 目录下的模板文件：
- `nl2sql.txt` - SQL生成
- `answer.txt` - 答案生成
- `critique.txt` - SQL修复

---

## ❓ 常见问题

### Q1: 如何切换LLM提供商？

修改 `.env` 文件：
```bash
LLM_PROVIDER=qwen  # 改为qwen或openai
QWEN_API_KEY=sk-xxxxx
```

### Q2: 如何使用自己的数据库？

修改 `.env` 配置：
```bash
DB_TYPE=postgresql
DB_HOST=your-host
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
```

### Q3: 如何提高SQL生成准确率？

1. 完善Schema信息（表注释、字段注释）
2. 添加领域相关的Few-shot示例
3. 构建行业术语词典
4. 收集历史SQL模板

### Q4: 支持哪些数据库？

- ✅ SQLite（演示/开发）
- ✅ PostgreSQL（生产推荐）
- ✅ MySQL（支持）
- 🔄 Oracle/SQL Server（计划中）

### Q5: 如何查看详细日志？

```bash
# 查看日志文件
tail -f logs/*.log

# 查看Docker日志
docker-compose logs -f nl2sql-api
```

---

## 🗺️ 路线图

### ✅ 已完成
- [x] 基础NL2SQL功能
- [x] Schema感知
- [x] SQL校验与修复
- [x] 安全沙箱
- [x] RAG检索增强
- [x] 多轮对话
- [x] 多表JOIN支持
- [x] 答案生成
- [x] 系统评测
- [x] 日志追踪
- [x] Web API
- [x] Docker部署

### 🚧 进行中
- [ ] 更多数据库支持（Oracle, SQL Server）
- [ ] 查询优化建议
- [ ] SQL explain分析

### 📋 计划中
- [ ] 多语言支持（英文、日文）
- [ ] 可视化查询构建器
- [ ] 查询结果可视化（图表）
- [ ] 用户认证与权限管理
- [ ] 查询历史管理
- [ ] Kubernetes部署支持

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 强大的Agent框架
- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用开发框架
- [Chinook Database](https://github.com/lerocha/chinook-database) - 优秀的示例数据库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架

---

## 📧 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱: your-email@example.com

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star！⭐**

Made with ❤️ by NL2SQL Team

</div>
