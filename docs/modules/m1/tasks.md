# M1 实践任务

完成以下任务，巩固 M1 模块的知识点。

::: tip 学习建议
- 按顺序完成任务
- 每个任务都要实际运行代码
- 记录遇到的问题和解决方案
- 对比不同 Prompt 的效果
:::

## 任务 1: 环境搭建与测试

### 目标

确保开发环境正确配置，能够成功调用 LLM。

### 步骤

#### 1.1 切换到 M1 分支

```bash
# 如果还没有切换
git checkout 01-prompt-nl2sql

# 确认分支
git branch
# 应该显示: * 01-prompt-nl2sql
```

#### 1.2 配置 API Key

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 文件
# Windows:
notepad .env

# Mac/Linux:
vim .env
```

**配置内容**（选择一个提供商）：

**选项 A: DeepSeek（推荐国内用户）**
```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx  # 替换成你的 API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

**选项 B: Qwen**
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxx
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
```

**选项 C: OpenAI**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

#### 1.3 测试配置

```bash
# 测试配置加载
python configs/config.py
```

**预期输出**：
```
=== NL2SQL 配置测试 ===

LLM 配置:
  提供商: deepseek
  模型: deepseek-chat
  API Key 已设置: 是
```

#### 1.4 测试 LLM Client

```bash
python tools/llm_client.py
```

**预期输出**：
```
✓ LLM Client initialized: deepseek (deepseek-chat)
Testing simple chat...
Response: SELECT * FROM users;
✓ Chat test passed
```

### 验收标准

- ✅ API Key 配置成功
- ✅ 配置测试通过
- ✅ LLM Client 测试通过
- ✅ 能看到 LLM 的正常响应

### 常见问题

**问题 1**: `ModuleNotFoundError: No module named 'configs'`

**解决**：确保在项目根目录运行命令
```bash
cd C:\Users\Administrator\Desktop\Jaguarliu\code\rookie-nl2sql
python tools/llm_client.py
```

**问题 2**: `Error: No API key provided`

**解决**：检查 `.env` 文件，确保对应提供商的 API Key 已设置

**问题 3**: `Connection timeout`

**解决**：检查网络连接，如果使用 OpenAI 可能需要代理

---

## 任务 2: 理解 Prompt 模板

### 目标

深入理解 M1 的 NL2SQL Prompt 结构。

### 步骤

#### 2.1 阅读 Prompt 模板

```bash
# 查看模板内容
cat prompts/nl2sql.txt

# Windows:
type prompts\nl2sql.txt
```

#### 2.2 分析模板结构

**任务**：回答以下问题

1. Prompt 分为哪几个部分？
2. Few-shot 示例有几个？分别教会了什么？
3. 为什么要明确"只返回SQL语句，不要解释"？
4. `{schema}` 和 `{question}` 是如何被填充的？

#### 2.3 手动填充模板

创建测试脚本 `test_prompt.py`：

```python
from pathlib import Path

# 读取模板
template_path = Path("prompts/nl2sql.txt")
with open(template_path, "r", encoding="utf-8") as f:
    template = f.read()

# 填充变量
schema = """
users (user_id, name, email, city)
orders (order_id, user_id, amount, order_date)
"""

question = "查询北京的用户数量"

# 生成最终 Prompt
prompt = template.format(
    schema=schema.strip(),
    question=question
)

print("=== 最终 Prompt ===")
print(prompt)
print("\n=== Prompt 长度 ===")
print(f"{len(prompt)} 字符")
```

运行：
```bash
python test_prompt.py
```

#### 2.4 分析 Prompt 长度

**任务**：统计 Prompt 的 token 数量

使用 `tiktoken` 库：
```bash
pip install tiktoken
```

```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
tokens = encoding.encode(prompt)

print(f"Token 数量: {len(tokens)}")
print(f"预估成本 (DeepSeek): {len(tokens) * 0.001 / 1000:.4f} 元")
```

### 验收标准

- ✅ 能够说出 Prompt 的 6 个部分
- ✅ 理解每个 Few-shot 示例的作用
- ✅ 能够手动填充模板
- ✅ 了解 Prompt 的长度和成本

---

## 任务 3: SQL 生成测试

### 目标

测试不同问题类型的 SQL 生成效果。

### 步骤

#### 3.1 运行 SQL 生成节点

```bash
python graphs/nodes/generate_sql.py
```

**观察输出**：
- LLM 原始响应
- 提取的 SQL
- 是否符合预期

#### 3.2 测试不同问题类型

创建 `test_sql_generation.py`：

```python
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from graphs.state import NL2SQLState
from graphs.nodes.generate_sql import generate_sql_node

test_cases = [
    # 简单查询
    "查询所有客户",

    # 条件查询
    "查询来自北京的客户",

    # 聚合查询
    "统计每个城市的客户数量",

    # 排序查询
    "查询销售额最高的前10个客户",

    # 复杂查询
    "查询每个客户的总订单金额，按金额降序排列",

    # 英文查询
    "Show all customers from Beijing",

    # 模糊查询
    "找出名字里包含'张'的客户",

    # 时间查询
    "查询2024年1月的所有订单",
]

print("=== SQL 生成测试 ===\n")

results = []

for i, question in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"测试用例 {i}/{len(test_cases)}")
    print(f"{'='*60}")

    state: NL2SQLState = {
        "question": question,
        "session_id": f"test-{i}",
        "timestamp": None,
        "intent": None,
        "candidate_sql": None,
        "sql_generated_at": None
    }

    result = generate_sql_node(state)

    sql = result.get("candidate_sql", "")

    # 简单验证
    is_valid = (
        sql and
        "SELECT" in sql.upper() and
        ";" in sql
    )

    results.append({
        "question": question,
        "sql": sql,
        "valid": is_valid
    })

    print(f"\n状态: {'✓ 成功' if is_valid else '✗ 失败'}")

# 统计
print(f"\n\n{'='*60}")
print("测试总结")
print(f"{'='*60}")

success = sum(1 for r in results if r["valid"])
total = len(results)

print(f"成功: {success}/{total}")
print(f"失败: {total - success}/{total}")
print(f"成功率: {success/total*100:.1f}%")

# 显示失败案例
failed = [r for r in results if not r["valid"]]
if failed:
    print(f"\n失败案例:")
    for r in failed:
        print(f"  - {r['question']}")
        print(f"    SQL: {r['sql']}")
```

运行：
```bash
python test_sql_generation.py
```

#### 3.3 分析结果

**任务**：

1. 哪些类型的问题生成效果好？
2. 哪些类型的问题生成效果差？
3. 为什么会出现失败案例？
4. 如何改进 Prompt 来提升成功率？

### 验收标准

- ✅ 成功率 ≥ 60%
- ✅ 能够分析失败原因
- ✅ 提出改进方案

---

## 任务 4: Prompt 优化实验

### 目标

通过调整 Prompt，提升 SQL 生成质量。

### 步骤

#### 4.1 创建 Prompt 变体

复制模板：
```bash
cp prompts/nl2sql.txt prompts/nl2sql_v2.txt
```

#### 4.2 优化方向（选择一个）

**方向 1: 添加更多 Few-shot 示例**

在 `nl2sql_v2.txt` 中添加：
```
### 示例 6: 模糊查询
问题: 查询名字包含"张"的客户
SQL:
```sql
SELECT * FROM customers WHERE customer_name LIKE '%张%';
```

### 示例 7: 时间范围查询
问题: 查询2024年1月的订单
SQL:
```sql
SELECT * FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01';
```
```

**方向 2: 更详细的输出要求**

修改"要求"部分：
```
## 要求
1. **只返回SQL语句**，不要有任何解释或说明
2. 使用标准SQL语法
3. 确保列名和表名与Schema完全一致
4. 如果需要聚合，使用GROUP BY
5. 如果需要排序，使用ORDER BY
6. 如果需要限制数量，使用LIMIT
7. SQL语句必须以分号结尾
8. **对于模糊查询，使用LIKE操作符**
9. **对于时间查询，使用日期比较（>=, <）**
10. **对于多条件查询，使用AND/OR连接**
```

**方向 3: 添加负面示例**

在 Few-shot 示例后添加：
```
## 错误示例

### ❌ 错误做法 1: 包含解释
问题: 查询所有客户
SQL: 以下是查询所有客户的SQL语句：SELECT * FROM customers;

原因: 不要包含任何解释文字

### ✅ 正确做法
问题: 查询所有客户
SQL: SELECT * FROM customers;

### ❌ 错误做法 2: 表名不存在
问题: 查询所有用户
SQL: SELECT * FROM users;

原因: 根据Schema，应该使用 customers 表，不是 users

### ✅ 正确做法
问题: 查询所有用户
SQL: SELECT * FROM customers;
```

#### 4.3 修改代码使用新 Prompt

修改 `graphs/nodes/generate_sql.py:92`：
```python
# 原来
prompt_template = load_prompt_template("nl2sql")

# 改为
prompt_template = load_prompt_template("nl2sql_v2")
```

#### 4.4 A/B 测试

创建 `test_prompt_ab.py`：

```python
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.llm_client import llm_client
from graphs.nodes.generate_sql import load_prompt_template, extract_sql_from_response

# 测试用例
test_questions = [
    "查询名字包含'张'的客户",
    "查询2024年1月的订单",
    "查询北京或上海的客户",
    "统计每个城市客户数量，按数量降序",
]

schema_placeholder = """
customers (customer_id, customer_name, city, country)
orders (order_id, customer_id, amount, order_date)
"""

print("=== Prompt A/B 测试 ===\n")

for question in test_questions:
    print(f"\n问题: {question}")
    print(f"{'-'*60}")

    # 测试版本 1
    template_v1 = load_prompt_template("nl2sql")
    prompt_v1 = template_v1.format(schema=schema_placeholder.strip(), question=question)
    response_v1 = llm_client.chat(prompt_v1)
    sql_v1 = extract_sql_from_response(response_v1)

    # 测试版本 2
    template_v2 = load_prompt_template("nl2sql_v2")
    prompt_v2 = template_v2.format(schema=schema_placeholder.strip(), question=question)
    response_v2 = llm_client.chat(prompt_v2)
    sql_v2 = extract_sql_from_response(response_v2)

    print(f"版本 1: {sql_v1}")
    print(f"版本 2: {sql_v2}")

    if sql_v1 != sql_v2:
        print("⚠️  两个版本的结果不同")
    else:
        print("✓ 两个版本的结果相同")
```

运行：
```bash
python test_prompt_ab.py
```

#### 4.5 对比分析

**任务**：

1. 哪个版本的成功率更高？
2. 新增的示例/要求是否有效？
3. 两个版本各有什么优缺点？

### 验收标准

- ✅ 创建了至少 1 个 Prompt 变体
- ✅ 进行了 A/B 对比测试
- ✅ 有明确的数据支持结论
- ✅ 能说明哪个版本更好以及原因

---

## 任务 5: 运行完整图

### 目标

运行完整的 NL2SQL 图，理解端到端流程。

### 步骤

#### 5.1 运行基础图

```bash
python graphs/base_graph.py
```

**观察输出**：
- Parse Intent 节点的输出
- Generate SQL 节点的输出
- Echo 节点的汇总信息

#### 5.2 自定义测试问题

修改 `graphs/base_graph.py:147-151`：

```python
test_questions = [
    "查询所有客户的订单总额",
    "统计每个国家的客户数量",
    "查询订单金额大于1000的客户名字",
    # 添加你自己的测试问题
    "你的问题1",
    "你的问题2",
]
```

重新运行：
```bash
python graphs/base_graph.py
```

#### 5.3 理解 State 流转

**任务**：画出 State 在各节点间的流转

```
初始 State:
{
  question: "查询所有客户",
  session_id: "xxx",
  timestamp: None,
  intent: None,
  candidate_sql: None,
  sql_generated_at: None
}

↓ parse_intent

State (after parse_intent):
{
  question: "查询所有客户",
  session_id: "xxx",
  timestamp: "2024-01-15T10:30:00",
  intent: {...},  # ← 新增
  candidate_sql: None,
  sql_generated_at: None
}

↓ generate_sql

State (after generate_sql):
{
  question: "查询所有客户",
  session_id: "xxx",
  timestamp: "2024-01-15T10:30:00",
  intent: {...},
  candidate_sql: "SELECT * FROM customers;",  # ← 新增
  sql_generated_at: "2024-01-15T10:30:05"     # ← 新增
}

↓ echo → END
```

### 验收标准

- ✅ 成功运行完整图
- ✅ 理解每个节点的作用
- ✅ 能够画出 State 流转图
- ✅ 添加了自定义测试问题

---

## 任务 6: 验收测试

### 目标

通过 M1 的验收测试。

### 步骤

#### 6.1 运行验收测试

```bash
python tests/test_m1_acceptance.py
```

#### 6.2 分析测试结果

**如果通过率 < 70%**：

1. 查看失败的测试用例
2. 分析失败原因（表名错误、SQL 语法错误、输出格式问题）
3. 调整 Prompt 模板
4. 重新运行测试

**优化技巧**：

- 添加相关的 Few-shot 示例
- 更明确的输出格式要求
- 尝试不同的模型（qwen-max, gpt-4）

#### 6.3 记录结果

创建 `m1_test_report.md`：

```markdown
# M1 验收测试报告

## 测试环境

- LLM 提供商: deepseek/qwen/openai
- 模型: deepseek-chat/qwen-plus/gpt-3.5-turbo
- 测试时间: 2024-01-15

## 测试结果

- 总用例数: 10
- 通过数: 7
- 失败数: 3
- 通过率: 70.0%

## 失败案例

### 案例 1
- 问题: 查询价格在100到500之间的产品
- 期望: `BETWEEN`
- 实际: `price >= 100 AND price <= 500`
- 原因: 语义正确但关键词不匹配
- 改进: 添加 BETWEEN 的示例

### 案例 2
...

## 优化建议

1. 添加 BETWEEN 的 Few-shot 示例
2. 明确 Schema 中的表名（M3 会解决）
3. ...

## 结论

✓ 通过验收标准（≥70%）
```

### 验收标准

- ✅ 验收测试通过率 ≥ 70%
- ✅ 完成测试报告
- ✅ 记录失败案例和改进建议

---

## 任务 7: 切换 LLM 提供商（可选）

### 目标

体验不同 LLM 提供商的效果差异。

### 步骤

#### 7.1 准备多个 API Key

如果可以，准备 DeepSeek、Qwen、OpenAI 的 API Key。

#### 7.2 测试不同提供商

创建 `test_providers.py`：

```python
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.llm_client import LLMClient

test_question = "查询销售额最高的前10个客户"

providers = ["deepseek", "qwen", "openai"]

print("=== LLM 提供商对比测试 ===\n")

for provider in providers:
    # 检查 API Key
    api_key_env = f"{provider.upper()}_API_KEY"
    if not os.getenv(api_key_env):
        print(f"⚠️  跳过 {provider}（未配置 API Key）")
        continue

    print(f"\n{'='*60}")
    print(f"提供商: {provider}")
    print(f"{'='*60}")

    try:
        client = LLMClient(provider=provider)

        # 简单 Prompt
        response = client.chat(
            prompt=f"将这句话转成SQL: {test_question}",
            system_message="你是SQL专家，只返回SQL"
        )

        print(f"响应: {response}")

    except Exception as e:
        print(f"✗ 错误: {e}")

print("\n=== 测试完成 ===")
```

运行：
```bash
python test_providers.py
```

#### 7.3 对比分析

**任务**：对比不同提供商的：

1. **响应速度**：哪个最快？
2. **SQL 质量**：哪个最准确？
3. **成本**：哪个最便宜？
4. **稳定性**：哪个最稳定？

### 验收标准

- ✅ 至少测试 2 个提供商
- ✅ 对比了响应质量
- ✅ 有明确的结论

---

## 任务 8: 文档学习（必做）

### 目标

深入理解提示词工程和 LLM Client 设计。

### 步骤

#### 8.1 阅读提示词工程文档

阅读 [提示词工程详解](./prompt-engineering.md)，回答：

1. Prompt 设计的 6 个原则是什么？
2. Few-shot Learning 与 Zero-shot 的区别？
3. 如何评估 Prompt 质量？
4. M1 的 5 个 Few-shot 示例分别教会了什么？

#### 8.2 阅读 LLM Client 文档

阅读 [LLM Client 设计](./llm-client.md)，回答：

1. 为什么需要 LLM Client？
2. 配置管理的优先级是什么？
3. 如何扩展新的 LLM 提供商？
4. 全局实例的优势是什么？

### 验收标准

- ✅ 完整阅读两篇文档
- ✅ 能够回答上述问题

---

## 挑战任务（进阶）

### 挑战 1: 动态 Few-shot 选择

根据问题类型，动态选择相关的 Few-shot 示例。

**提示**：
```python
def get_relevant_examples(question):
    if "统计" in question or "数量" in question:
        return aggregation_examples
    elif "排序" in question or "最" in question:
        return ranking_examples
    else:
        return basic_examples
```

### 挑战 2: Prompt Token 优化

在保持效果的前提下，减少 Prompt 的 Token 数量。

**目标**：Token 数量减少 30%，准确率下降 < 5%

### 挑战 3: 多模型投票

使用多个模型生成 SQL，然后投票选择最佳结果。

**提示**：
```python
models = ["deepseek", "qwen", "openai"]
results = []

for model in models:
    client = LLMClient(provider=model)
    sql = generate_sql(client, question)
    results.append(sql)

# 投票：选择出现次数最多的 SQL
final_sql = max(set(results), key=results.count)
```

### 挑战 4: 自动 Prompt 优化

编写脚本，自动调整 Prompt 并测试效果。

**提示**：
1. 准备多个 Prompt 变体
2. 在测试集上运行
3. 选择效果最好的版本

---

## 总结

完成以上任务后，你应该掌握：

- ✅ 提示词工程基础
- ✅ Few-shot Learning 技术
- ✅ LLM Client 封装和使用
- ✅ SQL 生成调试和优化
- ✅ A/B 测试方法
- ✅ 多提供商对比

**下一步**：
- 👉 [M2: Function Call 数据库操作](/modules/m2/overview.md)
- 👉 [返回 M1 概述](./overview.md)
