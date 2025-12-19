# 项目结构设计

本文详细介绍 M0 模块搭建的项目结构，以及每个目录和文件的职责。

## 整体结构

```
rookie-nl2sql/
├── graphs/                    # 🎯 LangGraph 核心
├── configs/                   # ⚙️  配置管理
├── tools/                     # 🔧 工具函数
├── prompts/                   # 📝 提示词模板
├── tests/                     # ✅ 测试代码
├── data/                      # 💾 数据文件
├── docs/                      # 📖 课程文档
├── .env.example               # 🔐 环境变量模板
├── requirements.txt           # 📦 Python 依赖
└── README.md                  # 📘 项目说明
```

## 核心目录详解

### graphs/ - LangGraph 核心

这是整个系统的**大脑**，所有的业务逻辑都在这里。

```
graphs/
├── __init__.py
├── state.py                  # State 定义
├── base_graph.py             # 基础图实现
└── nodes/                    # 节点实现（M1+）
    ├── __init__.py
    ├── parse_intent.py       # 意图解析节点
    ├── generate_sql.py       # SQL生成节点（M1）
    ├── validate_sql.py       # SQL校验节点（M4）
    └── execute_sql.py        # SQL执行节点（M2）
```

**设计原则**：

1. **state.py**: 所有 State 定义放在一起，便于维护
2. **base_graph.py**: M0 的简单图，后续模块会扩展
3. **nodes/**: 每个节点一个文件，职责单一

**示例**：

```python
# graphs/state.py
class NL2SQLState(TypedDict):
    question: str
    intent: Optional[Dict]
    # M1+: 添加更多字段
    # candidate_sql: Optional[str]
    # validation: Optional[Dict]
```

```python
# graphs/nodes/parse_intent.py
def parse_intent_node(state: NL2SQLState) -> NL2SQLState:
    """独立的意图解析节点"""
    # 实现逻辑
    return updated_state
```

### configs/ - 配置管理

管理所有配置，包括 LLM、数据库、RAG 等。

```
configs/
├── __init__.py
├── config.py                 # 配置加载器
├── dev.yaml                  # 开发环境配置
└── prod.yaml                 # 生产环境配置（M13）
```

**核心文件**：

#### config.py

```python
class Config:
    def __init__(self, env: str = "dev"):
        """加载 {env}.yaml 和 .env"""
        self._load_yaml_config()
        self._load_env_vars()

    def get_llm_config(self) -> Dict:
        """统一的 LLM 配置获取"""
        provider = self.get("llm_provider", "deepseek")
        # 根据 provider 返回对应配置
```

#### dev.yaml

```yaml
llm:
  provider: "deepseek"  # 默认使用 DeepSeek
  temperature: 0.0
  max_tokens: 2000

database:
  type: "sqlite"
  path: "data/chinook.db"

rag:
  enabled: false
  top_k: 5
```

**为什么这样设计？**

- ✅ **环境隔离**：dev.yaml, prod.yaml 分离
- ✅ **优先级明确**：环境变量 > YAML 配置
- ✅ **敏感信息保护**：API Key 不进 YAML，只在 .env
- ✅ **易于切换**：`Config(env="prod")` 即可切换环境

### tools/ - 工具函数

通用的工具函数，与业务逻辑解耦。

```
tools/
├── __init__.py
├── db.py                     # 数据库工具（M2）
├── retriever.py              # 向量检索（M6）
├── sql_validator.py          # SQL 校验（M4）
└── llm_client.py             # LLM 客户端封装（M1）
```

**设计原则**：

1. **纯函数**：输入输出明确，无副作用
2. **可测试**：易于单元测试
3. **可复用**：多个节点可以共用

**示例**（M2 模块）：

```python
# tools/db.py
class DatabaseTool:
    def __init__(self, db_path: str):
        self.engine = create_engine(f"sqlite:///{db_path}")

    def execute_query(self, sql: str) -> Dict:
        """执行 SQL 查询"""
        try:
            result = self.engine.execute(sql)
            return {"ok": True, "rows": result.fetchall()}
        except Exception as e:
            return {"ok": False, "error": str(e)}
```

### prompts/ - 提示词模板

所有 Prompt 模板集中管理，便于调优。

```
prompts/
├── nl2sql.txt                # SQL 生成 Prompt（M1）
├── critique.txt              # SQL 修复 Prompt（M4）
├── answer.txt                # 答案生成 Prompt（M9）
└── clarify.txt               # 澄清问题 Prompt（M7）
```

**为什么单独目录？**

- ✅ **版本管理**：Prompt 调优可以追踪历史
- ✅ **A/B测试**：可以有多个版本对比
- ✅ **易于编辑**：非代码人员也能优化 Prompt
- ✅ **模板复用**：多个地方可以引用同一模板

**示例**（M1 模块）：

```
# prompts/nl2sql.txt
你是一个 SQL 专家，请根据以下信息生成 SQL 查询：

## 数据库 Schema
{schema}

## 用户问题
{question}

## 要求
1. 只返回 SQL，不要解释
2. 使用标准 SQL 语法
3. 确保列名和表名正确

SQL:
```

### tests/ - 测试代码

每个模块都有对应的验收测试。

```
tests/
├── test_m0_acceptance.py     # M0 验收测试
├── test_m1_acceptance.py     # M1 验收测试
├── test_m2_acceptance.py     # M2 验收测试
└── ...
```

**验收测试模板**：

```python
# tests/test_m0_acceptance.py
def test_m0_acceptance():
    """M0 验收：输入问题，能正确解析意图"""
    result = run_query("查询所有用户")

    assert result.get("question") is not None
    assert result.get("intent") is not None
    assert result.get("intent").get("type") == "query"
```

**为什么重要？**

- ✅ **质量保证**：每个模块都有明确的验收标准
- ✅ **回归测试**：修改代码后快速验证
- ✅ **学习工具**：测试即示例，看懂测试就懂模块

### data/ - 数据文件

示例数据库、RAG 语料等。

```
data/
├── chinook.db                # 示例数据库（M2）
├── rag_corpus/               # RAG 语料（M6）
│   ├── domain_terms.jsonl    # 行业术语
│   └── qa_pairs.jsonl        # 问答对
└── vector_store/             # 向量数据库（M6）
```

**说明**：

- `chinook.db`: 经典的音乐商店数据库，包含客户、订单、歌曲等表
- `.gitignore` 会忽略这些数据文件（体积大）
- M2 模块会提供下载/初始化脚本

## 文件命名规范

### Python 文件

- **模块**: 小写+下划线，如 `base_graph.py`
- **类**: 大驼峰，如 `class NL2SQLState`
- **函数**: 小写+下划线，如 `def parse_intent_node`
- **常量**: 大写+下划线，如 `DEFAULT_TEMPERATURE`

### 配置文件

- **环境配置**: `{env}.yaml`，如 `dev.yaml`, `prod.yaml`
- **环境变量**: `.env` (不提交), `.env.example` (模板)

### 测试文件

- **验收测试**: `test_{module}_acceptance.py`
- **单元测试**: `test_{module}_unit.py`
- **集成测试**: `test_{module}_integration.py`

## 导入规范

### 推荐的导入方式

```python
# 标准库
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# 第三方库
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# 项目内部
from graphs.state import NL2SQLState
from configs.config import config
from tools.db import DatabaseTool
```

### 避免循环导入

```python
# ❌ 不好
# graphs/base_graph.py
from graphs.nodes.parse_intent import parse_intent_node

# graphs/nodes/parse_intent.py
from graphs.base_graph import some_function  # 循环导入!

# ✅ 好
# 让 base_graph 导入 nodes，nodes 不导入 base_graph
# 如需共享功能，放到 utils/
```

## 可扩展性设计

### 添加新节点

```python
# 1. 在 graphs/nodes/ 创建新文件
# graphs/nodes/new_feature.py
def new_feature_node(state: NL2SQLState) -> NL2SQLState:
    # 实现逻辑
    return updated_state

# 2. 在 base_graph.py 中添加
workflow.add_node("new_feature", new_feature_node)
workflow.add_edge("previous_node", "new_feature")
```

### 添加新配置

```yaml
# configs/dev.yaml
new_feature:
  enabled: true
  param1: "value1"
```

```python
# 使用
config.get("new_feature.enabled")
```

### 添加新工具

```python
# tools/new_tool.py
class NewTool:
    def do_something(self):
        pass

# 在节点中使用
from tools.new_tool import NewTool
tool = NewTool()
```

## 目录演进

### M0 时期

```
rookie-nl2sql/
├── graphs/
│   ├── state.py           # 基础 State
│   └── base_graph.py      # 简单的两节点图
├── configs/
│   ├── config.py
│   └── dev.yaml
└── tests/
    └── test_m0_acceptance.py
```

### M1-M3 扩展

```
rookie-nl2sql/
├── graphs/
│   ├── state.py           # ✨ 添加 candidate_sql 字段
│   ├── base_graph.py      # ✨ 添加 generate_sql 节点
│   └── nodes/
│       ├── generate_sql.py  # ✨ 新增
│       └── execute_sql.py   # ✨ 新增
├── prompts/
│   └── nl2sql.txt         # ✨ 新增
├── tools/
│   ├── llm_client.py      # ✨ 新增
│   └── db.py              # ✨ 新增
└── data/
    └── chinook.db         # ✨ 新增
```

### M13 完整系统

```
rookie-nl2sql/
├── graphs/              # 完整的图节点
├── configs/             # dev + prod 配置
├── tools/               # 所有工具函数
├── prompts/             # 所有 Prompt 模板
├── tests/               # 完整的测试套件
├── data/                # 数据库 + RAG 语料
├── apps/
│   └── api/             # ✨ FastAPI 服务
├── docker/
│   └── docker-compose.yml  # ✨ 容器化部署
└── scripts/
    ├── init_db.sh       # ✨ 数据库初始化
    └── deploy.sh        # ✨ 部署脚本
```

## 最佳实践

### 1. 职责分离

每个目录/文件只做一件事：
- `graphs/`: 只管流程编排
- `tools/`: 只管具体工具实现
- `prompts/`: 只管提示词模板

### 2. 依赖倒置

高层模块不依赖低层模块，都依赖抽象：

```python
# ✅ 好
class LLMClient(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> str:
        pass

class DeepSeekClient(LLMClient):
    def chat(self, prompt: str) -> str:
        # DeepSeek 实现

class QwenClient(LLMClient):
    def chat(self, prompt: str) -> str:
        # Qwen 实现

# 节点只依赖抽象
def generate_sql_node(state, llm: LLMClient):
    response = llm.chat(prompt)
```

### 3. 配置外部化

不要硬编码：

```python
# ❌ 不好
api_key = "sk-..."
model = "deepseek-chat"

# ✅ 好
from configs.config import config
llm_config = config.get_llm_config()
api_key = llm_config["api_key"]
model = llm_config["model"]
```

### 4. 测试优先

每个模块都应该有测试：

```
graphs/
  nodes/
    generate_sql.py
tests/
  nodes/
    test_generate_sql.py  # 对应的测试
```

## 总结

好的项目结构应该：

- ✅ **清晰**：目录结构一目了然
- ✅ **分离**：职责明确，耦合度低
- ✅ **可扩展**：添加新功能不影响现有代码
- ✅ **可测试**：每个模块都能独立测试
- ✅ **可维护**：新人能快速上手

M0 的项目结构为整个课程打下了坚实的基础！

---

**下一步**：
- 👉 [配置系统详解](./configuration.md)
- 👉 [LangGraph 基础](./langgraph-basics.md)
- 👉 [实践任务](./tasks.md)
