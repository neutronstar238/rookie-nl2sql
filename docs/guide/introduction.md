# 课程介绍

欢迎来到 **NL2SQL LangGraph 实战课程**！

本课程将带你从零开始，构建一个**生产级的自然语言转SQL系统**，系统掌握大语言模型与结构化数据库的结合方式。

## 课程背景

在AI时代，让普通用户通过自然语言查询数据库已成为重要需求。然而，构建一个**真正可用**的NL2SQL系统，远不止调用一次LLM那么简单。

你需要考虑：
- ❓ 如何让LLM理解复杂的数据库Schema？
- 🔍 生成的SQL如何保证正确性和安全性？
- 🤖 如何处理用户的模糊问题和行业黑话？
- 🔗 多表关联查询如何生成？
- 💬 如何将查询结果转为自然语言回答？
- 🚀 如何部署成可用的生产系统？

本课程将**系统化地回答这些问题**，带你构建一个完整的NL2SQL解决方案。

## 课程特色

### 🎯 系统化设计
不是零散的技巧拼凑，而是完整的**系统设计**。从脚手架到部署，13个模块渐进式递进，最终形成生产级系统。

### 💡 实战导向
每个模块都是一个**独立的Git分支**，有明确的：
- **知识点**：要学什么
- **代码实现**：怎么做
- **验收标准**：做得对不对
- **实践任务**：举一反三

### 🌏 国内友好
优先支持**DeepSeek**和**通义千问**：
- 无需科学上网
- 价格低廉（DeepSeek: ¥1/百万tokens）
- 性能优秀

同时兼容OpenAI API格式，可随时切换。

### 🔧 技术前沿
使用**LangGraph**构建Agent系统：
- 状态可控
- 流程可追踪
- 易于调试
- 支持复杂逻辑

比传统的Chain更适合构建生产级应用。

## 你将学到什么

### 核心技术
- ✅ **LangGraph**：状态图编排与Agent开发
- ✅ **提示词工程**：如何设计高质量的NL2SQL Prompt
- ✅ **Function Call**：工具调用与数据库操作
- ✅ **RAG技术**：检索增强生成，处理行业黑话
- ✅ **SQL校验**：语法验证与自动修复
- ✅ **安全沙箱**：数据库执行安全保护
- ✅ **Few-shot学习**：少样本提升SQL生成质量
- ✅ **多轮对话**：意图澄清与上下文管理

### 工程能力
- 📊 **评测体系**：如何测试NL2SQL系统
- 🔍 **可观测性**：日志、追踪与调试
- 🚀 **系统部署**：Docker容器化与配置管理
- 🎨 **接口设计**：FastAPI + 前端展示

### 系统思维
- 🏗️ 如何设计可扩展的AI系统架构
- 🔄 如何处理LLM的不确定性
- ⚡ 如何平衡性能与成本
- 🛡️ 如何确保系统安全与可靠

## 课程路线图

```mermaid
graph LR
    M0[M0 脚手架] --> M1[M1 提示词]
    M1 --> M2[M2 Function Call]
    M2 --> M3[M3 Schema感知]
    M3 --> M4[M4 SQL校验]
    M4 --> M5[M5 安全沙箱]
    M5 --> M6[M6 RAG增强]
    M6 --> M7[M7 多轮对话]
    M7 --> M8[M8 多表联结]
    M8 --> M9[M9 答案生成]
    M9 --> M10[M10 系统评测]
    M10 --> M11[M11 可观测性]
    M11 --> M12[M12 API & UI]
    M12 --> M13[M13 部署]

    style M0 fill:#e1f5ff
    style M1 fill:#e1f5ff
    style M2 fill:#e1f5ff
    style M3 fill:#e1f5ff
    style M4 fill:#fff3e0
    style M5 fill:#fff3e0
    style M6 fill:#fff3e0
    style M7 fill:#f3e5f5
    style M8 fill:#f3e5f5
    style M9 fill:#f3e5f5
    style M10 fill:#e8f5e9
    style M11 fill:#e8f5e9
    style M12 fill:#e8f5e9
    style M13 fill:#e8f5e9
```

**基础篇** (M0-M3)：搭建基础框架，实现最简单的NL2SQL
**增强篇** (M4-M6)：提升质量与安全性
**进阶篇** (M7-M9)：支持复杂场景
**工程篇** (M10-M13)：走向生产环境

## 学习方式

### 1️⃣ 按顺序学习
每个模块都基于前一个模块，建议**按顺序**学习。

### 2️⃣ 切换分支实践
```bash
# 学习M0
git checkout 00-scaffold
python tests/test_m0_acceptance.py

# 学习M1
git checkout 01-prompt-nl2sql
python tests/test_m1_acceptance.py
```

### 3️⃣ 完成实践任务
每个模块都有2-3个实践任务，动手做才能真正掌握。

### 4️⃣ 查看最终集成
```bash
git checkout main
```
看看所有模块集成后的完整系统。

## 课程时长

- **快速通关**：2周（每天2-3小时）
- **深度学习**：4周（每天1-2小时）
- **自定进度**：根据个人情况调整

## 前置要求

### 必须掌握
- ✅ Python基础（函数、类、装饰器）
- ✅ 基本SQL语法（SELECT、WHERE、JOIN）
- ✅ Git基础操作（clone、checkout、commit）

### 了解即可
- 🔸 LLM基础概念（知道什么是提示词即可）
- 🔸 LangChain框架（会在课程中教）
- 🔸 FastAPI（M12才用到）

### 环境准备
- Python 3.8+
- Git
- 代码编辑器（VS Code推荐）
- DeepSeek或Qwen API Key（[获取方式](/guide/setup)）

## 获取帮助

- 📖 **文档**：详细的模块文档和API说明
- 💻 **代码**：完整的可运行代码和注释
- ✅ **测试**：每个模块都有验收测试
- 🐛 **Issues**：GitHub提问与讨论

## 下一步

准备好了吗？让我们开始吧！

👉 [了解课程目标](/guide/objectives)
👉 [NL2SQL系统概述](/guide/nl2sql-overview)
👉 [环境准备](/guide/setup)
