# LangGraph NL2SQL 实战课程设计文档

## 一、课程总体目标
本课程旨在通过一个完整的实战项目——**基于 LangGraph 的 NL2SQL 系统构建**，系统讲解大语言模型与结构化数据库的结合方式。学员将从零开始搭建一个具备自然语言查询数据库能力的智能代理系统，逐步掌握提示词工程、Function Call、RAG 检索增强、意图消歧、SQL 校验与安全防护等核心技术。

---

## 二、课程结构
### 总体分支规划
每个分支代表一个独立的知识点与可验证功能模块，合并主分支后形成完整系统。

| 模块编号 | 模块名称 | 分支名 | 目标简介 |
|-----------|-----------|---------|------------|
| M0 | 项目脚手架与基线 | `00-scaffold` | 构建最小可运行 LangGraph 框架 |
| M1 | 提示词工程实现 NL2SQL | `01-prompt-nl2sql` | 让 LLM 从自然语言生成 SQL |
| M2 | Function Call 数据库操作 | `02-func-call-db` | 通过 Function Call 执行数据库读写 |
| M3 | Schema 感知与元数据管理 | `03-schema-ingestion` | 让模型理解数据库结构 |
| M4 | SQL 校验与自我修复 | `04-sql-guardrail` | 结构化校验与 LLM 修复机制 |
| M5 | 执行安全与沙箱 | `05-exec-sandbox` | 保护数据库安全、限制执行风险 |
| M6 | RAG 行业黑话与 QA-SQL 检索 | `06-rag-domain-qa` | 实现黑话识别与历史 SQL 复用 |
| M7 | 多轮澄清与意图消歧 | `07-dialog-clarify` | 提升系统对模糊问题的理解力 |
| M8 | 多表联结与少样本模板 | `08-join-fewshot` | 生成复杂 SQL，支持多表 JOIN |
| M9 | 结果解释与自然语言回答 | `09-answer-builder` | 将 SQL 执行结果转为自然语言答案 |
| M10 | 系统评测框架 | `10-eval-benchmark` | 建立标准化测试与性能曲线 |
| M11 | 系统观测与日志 | `11-observability` | 可追踪可回放的日志体系 |
| M12 | Web API 与最小前端 | `12-api-ui` | 快速部署可交互的演示系统 |
| M13 | 部署与配置 | `13-deploy` | 实现系统可复现部署 |
| MAIN | 主分支集成 | `main` | 最终可用 NL2SQL 系统 |

---

## 三、项目目录结构
```
nl2sql-langgraph/
  ├─ apps/
  │   └─ api/                # FastAPI 服务
  ├─ data/
  │   ├─ chinook.sql         # 示例数据库
  │   └─ rag_corpus/         # 黑话与 QA 数据集
  ├─ graphs/
  │   ├─ base_graph.py       # 基础 LangGraph
  │   └─ nodes/              # 各功能节点实现
  ├─ tools/
  │   ├─ db.py               # 数据库工具函数
  │   └─ retriever.py        # 向量检索模块
  ├─ prompts/
  │   ├─ nl2sql.txt
  │   ├─ critique.txt
  │   └─ answer.txt
  ├─ eval/
  │   ├─ cases.jsonl         # 测试集
  │   └─ runner.py
  ├─ configs/
  │   ├─ dev.yaml
  │   └─ prod.yaml
  ├─ scripts/
  │   ├─ load_db.sh
  │   └─ seed_rag.py
  ├─ tests/
  │   └─ test_smoke.py
  ├─ docker/
  │   └─ docker-compose.yml
  ├─ README.md
  └─ LICENSE
```

---

## 四、课程模块设计详情

### M0 00-scaffold（脚手架与基线）
**目标**：构建最小可运行 LangGraph 程序，具备基础输入输出与配置读取能力。

**关键点**：
- 构建基础 State 结构
- 搭建 `base_graph.py`（含一个输入与回显节点）
- 统一读取 `.env` 与 `configs/dev.yaml`

**产出**：能运行 `python graphs/base_graph.py` 完成输入输出测试。

**验收标准**：输入一句话，控制台能正确打印意图对象。

---

### M1 01-prompt-nl2sql（提示词工程）
**目标**：让 LLM 通过 Prompt 把自然语言转成 SQL 语句。

**关键点**：
- 设计 `nl2sql.txt` 模板，明确输入输出结构（JSON 格式）
- 添加少样本模板示例（select、group、where、order）
- 在 `node_generate_sql.py` 中实现提示词调用

**验收标准**：10 条单表查询的 exact match ≥ 70%。

---

### M2 02-func-call-db（数据库 Function Call）
**目标**：通过 Function Call 完成真实数据库查询。

**关键点**：
- 实现 `tools/db.py` 中的 `query(sql)` 方法
- 在 Graph 中实现 `execute` 节点
- 支持 Function Call 结构化执行（tool + args）

**验收标准**：所有查询能正确返回结果表格。

---

### M3 03-schema-ingestion（Schema 感知）
**目标**：让模型“只使用真实存在的表与列”。

**关键点**：
- 构建自动 schema 抽取脚本
- 生成 `schema.json` 并注入 prompt
- 支持字段检索匹配与表清单提示

**验收标准**：随机 10 个问题中“幻觉字段” ≤ 1 次。

---

### M4 04-sql-guardrail（校验与自修复）
**目标**：保证 SQL 输出正确并可自我修复。

**关键点**：
- 使用 `sqlglot` 进行语法验证
- 构建 `critique.txt` 让模型修复错误 SQL
- 图结构：`generate → validate → (fail) → critique → regenerate`

**验收标准**：3 个错误用例（列名错/聚合错/别名错）可自动修复。

---

### M5 05-exec-sandbox（安全与沙箱）
**目标**：执行安全防护与权限隔离。

**关键点**：
- 设置数据库只读账户
- 限制行数、超时与危险关键字
- 记录 SQL 执行日志与拦截原因

**验收标准**：恶意 SQL 被拒且返回结构化错误信息。

---

### M6 06-rag-domain-qa（RAG 行业黑话）
**目标**：让系统理解行业黑话并利用历史 SQL 经验。

**关键点**：
- 构建行业术语映射表与 QA 对应集
- 向量化存入 FAISS/Chroma
- 在生成 SQL 前检索关联模板增强提示词

**验收标准**：在黑话数据集上，生成正确率提升 ≥ 15%。

---

### M7 07-dialog-clarify（澄清与消歧）
**目标**：支持多轮交互与澄清问题。

**关键点**：
- 定义“需要澄清”的判据
- 生成封闭式澄清问句
- 支持状态循环与上下文更新

**验收标准**：多轮澄清后 SQL 正确率显著提升。

---

### M8 08-join-fewshot（多表联结）
**目标**：生成多表联结 SQL。

**关键点**：
- 根据外键关系生成可用 JOIN 路径
- 增强 Few-shot 模板（多表别名、联结类型）

**验收标准**：多表用例执行准确率 ≥ 70%。

---

### M9 09-answer-builder（答案生成）
**目标**：将 SQL 结果转成自然语言说明。

**关键点**：
- 通过 `answer.txt` 指导模型生成答案与表格摘要
- 添加“SQL 溯源”信息

**验收标准**：答案含结论、关键值和 SQL 说明，无编造字段。

---

### M10 10-eval-benchmark（评测框架）
**目标**：评测系统性能与进步。

**关键点**：
- 构建测试集 `cases.jsonl`
- 实现 `runner.py`：exact match + execution accuracy

**验收标准**：生成评测报告，包含各阶段指标变化。

---

### M11 11-observability（观测与日志）
**目标**：实现系统可追踪性。

**关键点**：
- 每节点输出结构化日志（输入、输出、耗时、token）
- TraceID 机制支持失败回放

**验收标准**：能追溯任意一次错误查询的完整链路。

---

### M12 12-api-ui（API 与前端）
**目标**：构建可交互 Demo。

**关键点**：
- FastAPI 提供 `/query` 接口
- 最小前端（Streamlit/HTML）展示结果与 SQL 折叠视图

**验收标准**：前端输入一句问题，能正确展示结果表格与 SQL。

---

### M13 13-deploy（部署与配置）
**目标**：完整交付可运行系统。

**关键点**：
- Docker Compose 一键部署
- Dev/Prod 环境区分
- 启动脚本自动导入数据与索引

**验收标准**：新机器 15 分钟内可跑通端到端 Demo。

---

## 五、LangGraph 主线拓扑
```
parse_intent → rag_enrich → generate_sql → validate_sql → (critique→regenerate)
    → execute_sql → answer_builder
```

**State 示例**：
```python
{
  "question": str,
  "normalized_question": str,
  "schema": dict,
  "rag_evidence": list,
  "candidate_sql": str,
  "validation": {"ok": bool, "errors": list},
  "execution": {"ok": bool, "rows": list, "head": list, "error": str},
  "answer": str,
  "trace": list
}
```

---

## 六、教学与作业安排
每个分支包含：
- `README.md`：步骤、关键代码、命令与验收
- `tasks.md`：实践任务（2~3 个）
- `quiz.md`：小测（3~5 题）
- `acceptance.sh`：自动验收脚本

---

## 七、评测与数据建议
- 示例数据库：Chinook 或 Sakila
- 黑话词典样例：
  - “铁粉” → 忠诚客户
  - “复购” → 再下单次数≥2
- 指标体系：Exact Match + Execution Accuracy

---

## 八、时间规划
| 周次 | 模块范围 | 阶段目标 |
|------|-----------|-----------|
| 第1周 | M0–M3 | 架构与基础实现 |
| 第2周 | M4–M6 | 功能强化与语义增强 |
| 第3周 | M7–M9 | 对话体验与结果解释 |
| 第4周 | M10–M13 | 评测、部署与发布 |

---

## 九、安全与合规说明
- 默认只读数据库连接。
- 所有 SQL 由模型生成并校验，不允许用户拼接 SQL。
- 环境变量统一通过 `.env` 注入，禁止提交密钥。

---

## 十、结语
本课程通过“LangGraph + LangChain + LLM + RAG + Function Call”的体系化组合，将从概念到生产级部署完整呈现 NL2SQL 智能代理的落地路径。每个分支都可独立演示、迭代、扩展，为学员提供可复现、可持续进化的项目模板。

