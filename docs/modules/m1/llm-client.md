# LLM Client 设计详解

本文深入讲解 M1 模块中的 LLM Client 封装，帮助你理解如何构建统一的、支持多提供商的 LLM 客户端。

## 为什么需要 LLM Client？

### 问题场景

在开发 NL2SQL 系统时，你可能面临这些问题：

**问题 1: 多个 LLM 提供商**
```python
# 使用 DeepSeek
from openai import OpenAI
client = OpenAI(api_key="sk-xxx", base_url="https://api.deepseek.com")

# 切换到 Qwen
client = OpenAI(api_key="sk-yyy", base_url="https://dashscope.aliyuncs.com/...")

# 切换到 OpenAI
client = OpenAI(api_key="sk-zzz")
```

每次切换都要改代码！

**问题 2: 配置分散**
```python
# API Key 硬编码
api_key = "sk-xxxxx"  # ❌ 不安全

# 配置散落各处
model = "deepseek-chat"
temperature = 0.0
max_tokens = 2000
```

**问题 3: 调用接口不统一**
```python
# 有时用这种
response = client.chat.completions.create(...)

# 有时用那种
response = client.invoke(...)

# 还要处理不同的响应格式
```

### LLM Client 的解决方案

✅ **统一接口**
```python
from tools.llm_client import llm_client

# 简单调用，不管什么提供商
response = llm_client.chat(prompt="查询所有用户")
```

✅ **配置集中管理**
```python
# .env 文件
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxx

# 代码中自动读取
llm_client = LLMClient()  # 自动加载配置
```

✅ **轻松切换提供商**
```bash
# 只需改 .env 文件
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-yyyyy

# 代码无需修改！
```

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────┐
│          NL2SQL Application                 │
│  (graphs/nodes/generate_sql.py)             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│          LLM Client (tools/llm_client.py)   │
│  • Unified Interface                        │
│  • Provider Abstraction                     │
│  • Message Formatting                       │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      Configuration (configs/config.py)      │
│  • Load .env + YAML                         │
│  • Provider Selection                       │
│  • Parameter Management                     │
└────────────────┬────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│DeepSeek │ │  Qwen   │ │ OpenAI  │
│   API   │ │   API   │ │   API   │
└─────────┘ └─────────┘ └─────────┘
```

### 设计原则

1. **单一职责**：LLM Client 只负责 LLM 调用，不处理业务逻辑
2. **依赖注入**：配置从外部注入，不硬编码
3. **开闭原则**：支持扩展新提供商，无需修改核心代码
4. **接口隔离**：提供简单的 `chat()` 接口，隐藏复杂性

## 核心实现

### 1. 配置管理（Config）

#### 配置加载流程

```python
class Config:
    def __init__(self, env: str = "dev"):
        self._load_yaml_config()  # 1. 加载 YAML
        self._load_env_vars()     # 2. 加载环境变量
```

**优先级**：环境变量 > YAML 配置

#### LLM 配置获取

`configs/config.py:108-145`

```python
def get_llm_config(self) -> Dict[str, Any]:
    """根据选择的提供商获取 LLM 配置"""
    provider = self.get("llm_provider", "deepseek").lower()

    config = {
        "provider": provider,
        "temperature": self.get("llm_temperature", 0.0),
        "max_tokens": self.get("llm_max_tokens", 2000),
        "timeout": self.get("llm_timeout", 30),
    }

    if provider == "deepseek":
        config.update({
            "api_key": self.get("deepseek_api_key"),
            "base_url": self.get("deepseek_base_url"),
            "model": self.get("deepseek_model"),
        })
    elif provider == "qwen":
        config.update({
            "api_key": self.get("qwen_api_key"),
            "base_url": self.get("qwen_base_url"),
            "model": self.get("qwen_model"),
        })
    elif provider == "openai":
        config.update({
            "api_key": self.get("openai_api_key"),
            "base_url": self.get("openai_base_url"),
            "model": self.get("openai_model"),
        })

    return config
```

**关键点**：
- 统一的配置结构
- 根据 `provider` 动态选择参数
- 提供默认值

### 2. LLM Client 封装

#### 初始化

`tools/llm_client.py:30-60`

```python
class LLMClient:
    def __init__(self, provider: Optional[str] = None):
        """初始化 LLM 客户端"""
        # 获取配置
        llm_config = config.get_llm_config()

        self.provider = llm_config["provider"]
        self.model = llm_config["model"]

        # 使用 LangChain 的 ChatOpenAI
        # 所有提供商都兼容 OpenAI API 格式
        self.client = ChatOpenAI(
            model=llm_config["model"],
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"],
            timeout=llm_config["timeout"]
        )
```

**为什么用 ChatOpenAI？**
- DeepSeek、Qwen 都兼容 OpenAI API 格式
- 只需改 `base_url` 和 `api_key`
- 统一的消息格式（SystemMessage, HumanMessage）

#### Chat 方法

`tools/llm_client.py:62-101`

```python
def chat(
    self,
    prompt: str,
    system_message: Optional[str] = None,
    **kwargs
) -> str:
    """发送消息并获取回复"""
    messages = []

    # 添加系统消息（可选）
    if system_message:
        messages.append(SystemMessage(content=system_message))

    # 添加用户消息
    messages.append(HumanMessage(content=prompt))

    # 调用 LLM
    response = self.client.invoke(messages)

    # 返回文本内容
    return response.content
```

**简化了什么？**

**原始方式**（复杂）：
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是SQL专家"},
        {"role": "user", "content": "查询所有用户"}
    ],
    temperature=0.0,
    max_tokens=2000
)

sql = response.choices[0].message.content
```

**封装后**（简单）：
```python
from tools.llm_client import llm_client

sql = llm_client.chat(
    prompt="查询所有用户",
    system_message="你是SQL专家"
)
```

### 3. 全局实例

`tools/llm_client.py:137-138`

```python
# 全局 LLM 客户端实例
llm_client = LLMClient()
```

**优势**：
- 项目中任何地方都可以 `from tools.llm_client import llm_client`
- 配置只加载一次
- 减少初始化开销

## 使用指南

### 基础用法

#### 1. 配置 API Key

```bash
# 复制模板
cp .env.example .env

# 编辑 .env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

#### 2. 简单调用

```python
from tools.llm_client import llm_client

# 最简单的调用
response = llm_client.chat("1+1等于多少？")
print(response)  # "2"
```

#### 3. 带系统消息

```python
response = llm_client.chat(
    prompt="将这句话翻译成SQL: 查询所有用户",
    system_message="你是一个SQL专家，擅长SQL翻译"
)
print(response)
# SELECT * FROM users;
```

### 高级用法

#### 1. 动态调整参数

```python
# 提高创造性（用于生成示例数据等）
response = llm_client.chat(
    prompt="生成5个示例用户名",
    temperature=0.8  # 覆盖默认的 0.0
)

# 限制输出长度
response = llm_client.chat(
    prompt="解释什么是NL2SQL",
    max_tokens=100  # 限制在 100 tokens
)
```

#### 2. 多轮对话

```python
messages = [
    {"role": "system", "content": "你是SQL专家"},
    {"role": "user", "content": "如何查询所有用户？"},
    {"role": "assistant", "content": "SELECT * FROM users;"},
    {"role": "user", "content": "如何只查询名字叫张三的用户？"}
]

response = llm_client.chat_with_messages(messages)
print(response)
# SELECT * FROM users WHERE name = '张三';
```

#### 3. 切换提供商

**方式 1：修改 .env**
```bash
# 从 DeepSeek 切换到 Qwen
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxxxxxxx
```

**方式 2：代码中临时切换**
```python
# 创建临时客户端
qwen_client = LLMClient(provider="qwen")
response = qwen_client.chat("测试问题")

# 全局客户端不受影响
deepseek_response = llm_client.chat("测试问题")
```

### 在 NL2SQL 中的使用

`graphs/nodes/generate_sql.py:109-116`

```python
def generate_sql_node(state: NL2SQLState) -> NL2SQLState:
    # 1. 构建 Prompt
    prompt_template = load_prompt_template("nl2sql")
    prompt = prompt_template.format(
        schema=schema_placeholder,
        question=state["question"]
    )

    # 2. 调用 LLM（使用全局 llm_client）
    response = llm_client.chat(prompt=prompt)

    # 3. 提取 SQL
    sql = extract_sql_from_response(response)

    return {**state, "candidate_sql": sql}
```

**为什么这么简洁？**
- LLM Client 隐藏了所有配置细节
- 不用关心用的是哪个提供商
- 专注于业务逻辑（Prompt 构建、SQL 提取）

## 支持的 LLM 提供商

### 1. DeepSeek（推荐国内用户）

**配置**：
```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

**优势**：
- ✅ 性价比高（便宜）
- ✅ 中文能力强
- ✅ API 兼容 OpenAI
- ✅ 国内访问快

**获取 API Key**：
- 注册：https://platform.deepseek.com
- 创建 API Key
- 充值（1元起）

### 2. Qwen（阿里云）

**配置**：
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxx
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
```

**模型选择**：
- `qwen-turbo`: 快速、便宜（适合开发测试）
- `qwen-plus`: 平衡（适合生产）
- `qwen-max`: 最强（适合复杂任务）

**优势**：
- ✅ 阿里云生态
- ✅ 中文优化
- ✅ 稳定性高

**获取 API Key**：
- 开通：https://dashscope.aliyun.com
- 创建 API Key

### 3. OpenAI

**配置**：
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

**模型选择**：
- `gpt-3.5-turbo`: 快速、便宜
- `gpt-4`: 强大、贵
- `gpt-4-turbo`: 快速版 GPT-4

**优势**：
- ✅ 最强大
- ✅ 生态完善

**劣势**：
- ❌ 贵
- ❌ 国内访问需代理

## 错误处理

### 常见错误

#### 错误 1: API Key 未配置

```
Error: No API key provided
```

**解决**：
```bash
# 检查 .env 文件
cat .env | grep API_KEY

# 确保对应提供商的 API Key 已设置
DEEPSEEK_API_KEY=sk-xxxxxxxx
```

#### 错误 2: 网络连接失败

```
Error: Connection timeout
```

**解决**：
1. 检查网络连接
2. 检查 `base_url` 是否正确
3. 如果是 OpenAI，检查是否需要代理

#### 错误 3: 提供商不支持

```
ValueError: Unsupported LLM provider: xxx
```

**解决**：
```bash
# 检查 LLM_PROVIDER 配置
# 只支持: deepseek, qwen, openai
LLM_PROVIDER=deepseek
```

### 代码中的错误处理

```python
def generate_sql_node(state: NL2SQLState) -> NL2SQLState:
    try:
        response = llm_client.chat(prompt=prompt)
        sql = extract_sql_from_response(response)

        return {
            **state,
            "candidate_sql": sql,
            "sql_generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"✗ Error generating SQL: {e}")

        return {
            **state,
            "candidate_sql": None,  # 标记失败
            "sql_generated_at": datetime.now().isoformat()
        }
```

**建议**：
- 总是用 try-except 包裹 LLM 调用
- 记录错误日志
- 返回明确的失败状态（`None` 或错误信息）

## 测试与验证

### 测试 LLM Client

```bash
# 运行测试脚本
python tools/llm_client.py
```

**预期输出**：
```
=== LLM Client Test ===

✓ LLM Client initialized: deepseek (deepseek-chat)

Current Provider: deepseek
Current Model: deepseek-chat

Testing simple chat...
Response: SELECT * FROM users;

✓ Chat test passed

=== Test Complete ===
```

### 测试配置加载

```bash
python configs/config.py
```

**预期输出**：
```
=== NL2SQL 配置测试 ===

环境: dev

系统配置:
  系统名称: Rookie NL2SQL
  系统版本: 0.1.0
  日志级别: INFO

LLM 配置:
  提供商: deepseek
  模型: deepseek-chat
  Base URL: https://api.deepseek.com
  API Key 已设置: 是
  Temperature: 0.0
  Max Tokens: 2000
```

### 单元测试示例

```python
import pytest
from tools.llm_client import LLMClient

def test_llm_client_initialization():
    """测试客户端初始化"""
    client = LLMClient()
    assert client.provider in ["deepseek", "qwen", "openai"]
    assert client.model is not None

def test_llm_client_chat():
    """测试基本对话"""
    client = LLMClient()
    response = client.chat("1+1=?")
    assert "2" in response

def test_llm_client_with_system_message():
    """测试系统消息"""
    client = LLMClient()
    response = client.chat(
        prompt="查询所有用户",
        system_message="你是SQL专家，只返回SQL语句"
    )
    assert "SELECT" in response.upper()
```

## 最佳实践

### 1. 使用全局实例

✅ **推荐**：
```python
from tools.llm_client import llm_client

response = llm_client.chat("问题")
```

❌ **不推荐**：
```python
from tools.llm_client import LLMClient

client = LLMClient()  # 每次都初始化
response = client.chat("问题")
```

**原因**：全局实例只初始化一次，节省资源。

### 2. 明确的系统消息

✅ **推荐**：
```python
response = llm_client.chat(
    prompt="查询所有用户",
    system_message="你是SQL专家。只返回SQL语句，不要解释。"
)
```

❌ **不推荐**：
```python
response = llm_client.chat("你是SQL专家，查询所有用户")
```

**原因**：区分角色定义和任务描述，Prompt 更清晰。

### 3. 控制温度参数

```python
# 确定性任务（SQL 生成）：temperature = 0.0
sql = llm_client.chat(
    prompt="查询所有用户",
    temperature=0.0  # 结果稳定
)

# 创造性任务（生成示例）：temperature = 0.7-0.9
examples = llm_client.chat(
    prompt="生成3个示例用户名",
    temperature=0.8  # 结果多样
)
```

### 4. 错误处理

```python
try:
    response = llm_client.chat(prompt)
except Exception as e:
    logger.error(f"LLM调用失败: {e}")
    # 降级策略
    return default_response
```

### 5. 成本控制

```python
# 限制输出长度
response = llm_client.chat(
    prompt="生成SQL",
    max_tokens=200  # 避免超长输出
)

# 使用便宜的模型（开发阶段）
# .env 中设置：
# QWEN_MODEL=qwen-turbo  # 而不是 qwen-max
```

## 扩展新提供商

如果你想添加新的 LLM 提供商（例如：讯飞星火、百度文心），只需以下步骤：

### 步骤 1: 添加环境变量

`.env.example`:
```bash
# 讯飞星火
SPARK_API_KEY=your_spark_api_key
SPARK_BASE_URL=https://spark-api.xf-yun.com/v1
SPARK_MODEL=spark-3.0
```

### 步骤 2: 更新 Config

`configs/config.py`:
```python
def _load_env_vars(self):
    self.env_config = {
        # ... 现有配置 ...

        # 讯飞星火
        "spark_api_key": os.getenv("SPARK_API_KEY", ""),
        "spark_base_url": os.getenv("SPARK_BASE_URL", ""),
        "spark_model": os.getenv("SPARK_MODEL", "spark-3.0"),
    }

def get_llm_config(self):
    # ... 现有代码 ...

    elif provider == "spark":
        config.update({
            "api_key": self.get("spark_api_key"),
            "base_url": self.get("spark_base_url"),
            "model": self.get("spark_model"),
        })
```

### 步骤 3: 使用新提供商

```bash
# .env
LLM_PROVIDER=spark
SPARK_API_KEY=sk-xxxxxx
```

**前提**：新提供商必须兼容 OpenAI API 格式！

## 总结

### LLM Client 的核心价值

1. **统一接口**：一个 `chat()` 方法搞定所有 LLM 调用
2. **配置集中**：所有配置在 `.env` 和 `dev.yaml` 中
3. **易于切换**：改一行配置即可切换提供商
4. **简化代码**：业务代码专注于逻辑，不处理 API 细节

### 关键文件

| 文件 | 作用 |
|------|------|
| `tools/llm_client.py` | LLM Client 实现 |
| `configs/config.py` | 配置加载和管理 |
| `.env` | 环境变量（API Keys） |
| `configs/dev.yaml` | 开发环境配置 |

### 下一步

- 👉 [M1 实践任务](./tasks.md)
- 👉 [返回 M1 概述](./overview.md)
- 👉 [提示词工程详解](./prompt-engineering.md)
