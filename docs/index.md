---
layout: home

hero:
  name: "NL2SQL LangGraph"
  text: "实战课程"
  tagline: 从零构建生产级自然语言转SQL系统
  actions:
    - theme: brand
      text: 开始学习
      link: /guide/introduction
    - theme: alt
      text: 查看模块
      link: /modules/
    - theme: alt
      text: GitHub
      link: https://github.com/yourusername/rookie-nl2sql

features:
  - icon: 🎯
    title: 系统化课程设计
    details: 13个渐进式模块，从脚手架到生产部署，涵盖NL2SQL系统的完整生命周期

  - icon: 🚀
    title: 实战导向
    details: 每个模块都有独立分支、验收标准和实践任务，边学边做

  - icon: 🌏
    title: 国内友好
    details: 支持DeepSeek和通义千问，无需科学上网，价格低廉

  - icon: 🔧
    title: LangGraph驱动
    details: 使用LangGraph构建可控、可追踪的AI Agent系统

  - icon: 📊
    title: 完整技术栈
    details: 提示词工程、Function Call、RAG、SQL校验、安全沙箱等核心技术

  - icon: 🎓
    title: 生产级质量
    details: 包含评测框架、可观测性、部署方案等企业级实践

---

## 课程模块

### 基础篇 (M0-M3)
- **M0 项目脚手架**: 构建最小可运行LangGraph系统
- **M1 提示词工程**: 使用Prompt实现NL2SQL
- **M2 Function Call**: 通过工具调用执行数据库操作
- **M3 Schema感知**: 让模型理解数据库结构

### 增强篇 (M4-M6)
- **M4 SQL校验**: 结构化校验与自我修复
- **M5 执行沙箱**: 数据库安全与风险控制
- **M6 RAG增强**: 行业黑话识别与历史SQL复用

### 进阶篇 (M7-M9)
- **M7 多轮对话**: 意图澄清与上下文管理
- **M8 多表联结**: 复杂SQL生成与Few-shot学习
- **M9 答案生成**: SQL结果转自然语言回答

### 工程篇 (M10-M13)
- **M10 系统评测**: 标准化测试与性能优化
- **M11 可观测性**: 日志、追踪与调试
- **M12 API & UI**: Web服务与交互界面
- **M13 部署上线**: Docker容器化与配置管理

## 快速开始

```bash
# 克隆项目
git clone https://github.com/yourusername/rookie-nl2sql.git
cd rookie-nl2sql

# 安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑.env，填入DeepSeek或Qwen API Key

# 运行M0测试
python tests/test_m0_acceptance.py
```

## 适合人群

- 想要了解NL2SQL系统构建的开发者
- 希望实践LangGraph的AI应用开发者
- 需要将LLM集成到数据查询场景的工程师
- 对Agent系统设计感兴趣的学习者

## 前置知识

- Python基础
- 基本SQL语法
- LLM基础概念（了解即可）
- Git基础操作

## 技术特色

- ✅ 支持国内LLM (DeepSeek/Qwen)
- ✅ 完整的分支式教学
- ✅ 每个模块独立可运行
- ✅ 标准化验收测试
- ✅ 生产级代码质量
- ✅ 详细的文档和注释
