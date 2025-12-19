# M0 实践任务

完成这些实践任务，巩固 M0 模块的知识点。

## 任务1: 扩展 State 定义

**目标**: 理解 State 设计原则，为后续模块做准备

**任务描述**:
在 `graphs/state.py` 中扩展 State，添加以下字段：

```python
class NL2SQLState(TypedDict):
    # 现有字段
    question: str
    intent: Optional[Dict[str, Any]]
    session_id: Optional[str]
    timestamp: Optional[str]

    # 👇 请添加以下字段
    # 用户信息（M7 多轮对话需要）
    user_id: Optional[str]

    # 对话历史（M7 需要）
    dialog_history: Optional[List[Dict]]

    # 候选 SQL（M1 需要）
    candidate_sql: Optional[str]

    # SQL 执行结果（M2 需要）
    execution_result: Optional[Dict]
```

**验收标准**:
1. State 定义语法正确
2. 所有字段都有类型注解
3. 运行 `python graphs/base_graph.py` 不报错

**提示**:
- 使用 `Optional[]` 标记可选字段
- 使用 `List[]`, `Dict[]` 等泛型类型
- 添加注释说明每个字段的用途

---

## 任务2: 添加日志节点

**目标**: 掌握节点编写和图构建

**任务描述**:
创建一个日志节点，记录每次查询的基本信息到文件。

### 步骤

**1. 创建节点函数**

在 `graphs/base_graph.py` 中添加：

```python
def log_node(state: NL2SQLState) -> NL2SQLState:
    """
    记录查询日志到文件
    """
    import json
    from pathlib import Path

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "query_log.jsonl"

    log_entry = {
        "session_id": state.get("session_id"),
        "question": state.get("question"),
        "intent": state.get("intent"),
        "timestamp": state.get("timestamp")
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    print(f"✓ Log written to {log_file}")

    return state
```

**2. 添加到图中**

修改 `build_graph()` 函数：

```python
def build_graph() -> StateGraph:
    workflow = StateGraph(NL2SQLState)

    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("log", log_node)  # 👈 添加日志节点
    workflow.add_node("echo", echo_node)

    workflow.set_entry_point("parse_intent")
    workflow.add_edge("parse_intent", "log")  # 👈 修改边
    workflow.add_edge("log", "echo")
    workflow.add_edge("echo", END)

    return workflow.compile()
```

**验收标准**:
1. 运行 `python graphs/base_graph.py`
2. 检查 `logs/query_log.jsonl` 文件是否生成
3. 日志内容包含所有必要字段

---

## 任务3: 实现配置切换

**目标**: 掌握配置系统使用

**任务描述**:
实现一个脚本，能够在不同 LLM 提供商之间切换。

### 步骤

**1. 创建测试脚本**

创建 `scripts/test_llm_config.py`:

```python
#!/usr/bin/env python
"""
测试 LLM 配置切换
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import Config

def test_llm_provider(provider: str):
    """测试特定 LLM 提供商配置"""
    # 临时设置环境变量
    os.environ["LLM_PROVIDER"] = provider

    # 重新加载配置
    config = Config()
    llm_config = config.get_llm_config()

    print(f"\n=== {provider.upper()} 配置 ===")
    print(f"Provider: {llm_config['provider']}")
    print(f"Model: {llm_config.get('model', 'N/A')}")
    print(f"Base URL: {llm_config.get('base_url', 'N/A')}")
    print(f"API Key Set: {'Yes' if llm_config.get('api_key') else 'No'}")

if __name__ == "__main__":
    providers = ["deepseek", "qwen", "openai"]

    print("=== LLM 配置切换测试 ===")

    for provider in providers:
        try:
            test_llm_provider(provider)
        except Exception as e:
            print(f"Error with {provider}: {e}")

    print("\n✓ 测试完成")
```

**2. 运行测试**

```bash
python scripts/test_llm_config.py
```

**验收标准**:
1. 能正确显示 DeepSeek, Qwen, OpenAI 三个提供商的配置
2. 切换 provider 能自动选择对应的 API Key 和 Model
3. 无报错

---

## 任务4: 创建自定义验收测试

**目标**: 掌握测试编写

**任务描述**:
编写一个新的验收测试，测试特定场景。

### 场景

测试系统对**中英文混合问题**的处理能力。

**1. 创建测试文件**

`tests/test_m0_bilingual.py`:

```python
"""
M0 双语测试：测试中英文混合问题
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from graphs.base_graph import run_query

def test_bilingual_questions():
    """测试中英文混合问题"""
    test_cases = [
        "查询 user 的订单",
        "Show me all 客户 in 北京",
        "统计 sales by region"
    ]

    print("=== M0 双语测试 ===\n")

    passed = 0
    for i, question in enumerate(test_cases, 1):
        print(f"Test Case {i}: {question}")

        result = run_query(question)

        # 验证基本字段存在
        assert result.get("question") == question
        assert result.get("intent") is not None
        assert result.get("session_id") is not None

        # 验证 intent 包含必要信息
        intent = result.get("intent")
        assert "type" in intent
        assert "question_length" in intent

        print(f"✓ Test Case {i} passed\n")
        passed += 1

    print(f"=== 测试结果: {passed}/{len(test_cases)} passed ===")

if __name__ == "__main__":
    test_bilingual_questions()
```

**2. 运行测试**

```bash
python tests/test_m0_bilingual.py
```

**验收标准**:
1. 所有测试用例通过
2. 中英文混合问题能正确解析
3. 输出清晰，易于理解

---

## 任务5: 优化意图识别（进阶）

**目标**: 深入理解节点逻辑

**任务描述**:
扩展 `parse_intent_node`，实现更智能的意图识别。

### 需求

当前的意图识别只是简单的关键词匹配，请实现：

1. **识别问题类型**：统计类、查询类、排序类
2. **提取关键信息**：表名、字段名、数量词
3. **检测时间范围**：是否包含时间限制

**示例代码**：

```python
def parse_intent_node(state: NL2SQLState) -> NL2SQLState:
    """
    增强版意图解析
    """
    question = state.get("question", "")
    question_lower = question.lower()

    # 1. 识别问题类型
    if any(kw in question_lower for kw in ["统计", "多少", "总计", "count", "sum"]):
        question_type = "aggregation"
    elif any(kw in question_lower for kw in ["排名", "top", "前", "最"]):
        question_type = "ranking"
    elif any(kw in question_lower for kw in ["查询", "显示", "show", "select"]):
        question_type = "select"
    else:
        question_type = "unknown"

    # 2. 提取数量词
    import re
    numbers = re.findall(r'\d+', question)
    limit = int(numbers[0]) if numbers else None

    # 3. 检测时间范围
    has_time = any(kw in question_lower
                   for kw in ["今天", "本月", "本年", "yesterday", "last"])

    intent = {
        "type": question_type,
        "limit": limit,
        "has_time_range": has_time,
        "question_length": len(question),
        "parsed_at": datetime.now().isoformat()
    }

    print(f"\n=== Enhanced Intent ===")
    print(f"Type: {question_type}")
    print(f"Limit: {limit}")
    print(f"Has Time Range: {has_time}")

    return {
        **state,
        "intent": intent,
        "timestamp": datetime.now().isoformat()
    }
```

**验收标准**:
1. 能正确识别统计、排序、查询三种类型
2. 能提取数量限制（如"前10个"中的10）
3. 能检测时间范围关键词
4. 运行原有验收测试仍然通过

---

## 提交你的作业

完成任务后，欢迎分享你的代码和心得：

1. Fork 项目仓库
2. 创建你的分支: `git checkout -b feat/m0-task-yourname`
3. 提交你的改动: `git commit -m "完成M0实践任务"`
4. Push 到你的仓库: `git push origin feat/m0-task-yourname`
5. 创建 Pull Request

**或者**：

在 GitHub Issues 中分享你的学习心得和遇到的问题！

---

## 挑战任务（可选）

### 挑战1: 实现条件路由

在图中添加条件边，根据 intent 类型路由到不同节点。

```python
def route_by_intent(state: NL2SQLState) -> str:
    """根据 intent 类型路由"""
    intent_type = state.get("intent", {}).get("type")

    if intent_type == "aggregation":
        return "aggregation_handler"
    elif intent_type == "ranking":
        return "ranking_handler"
    else:
        return "general_handler"

# 添加条件边
workflow.add_conditional_edges(
    "parse_intent",
    route_by_intent,
    {
        "aggregation_handler": aggregation_node,
        "ranking_handler": ranking_node,
        "general_handler": general_node
    }
)
```

### 挑战2: 实现配置热重载

允许在不重启程序的情况下重新加载配置。

```python
class Config:
    def reload(self):
        """重新加载配置"""
        self._load_yaml_config()
        self._load_env_vars()
        print("✓ Configuration reloaded")
```

### 挑战3: 添加性能监控

在每个节点添加性能监控，记录执行时间。

```python
import time
from functools import wraps

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(state):
        start = time.time()
        result = func(state)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@monitor_performance
def parse_intent_node(state):
    # 原有逻辑
    pass
```

---

**完成这些任务后，你就真正掌握了 M0 的核心知识！**

准备好继续学习了吗？

👉 [M1: 提示词工程](/modules/m1/overview.md)
