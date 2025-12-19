# 环境准备

开始学习前，请确保你的开发环境已经准备就绪。

## 系统要求

### 操作系统
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, CentOS 8+)

### 软件要求
- **Python**: 3.8 或更高版本
- **Git**: 2.0 或更高版本
- **代码编辑器**: VS Code 推荐（或任何你喜欢的编辑器）

## 安装步骤

### 1. 安装 Python

#### Windows
从 [python.org](https://www.python.org/downloads/) 下载并安装。

**验证安装**:
```bash
python --version  # 应显示 Python 3.8+
```

#### macOS
```bash
# 使用 Homebrew
brew install python@3.11
```

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### 2. 安装 Git

#### Windows
从 [git-scm.com](https://git-scm.com/) 下载并安装。

#### macOS
```bash
brew install git
```

#### Linux
```bash
sudo apt install git
```

**验证安装**:
```bash
git --version  # 应显示 git version 2.x
```

### 3. 克隆项目

```bash
# 克隆仓库
git clone https://github.com/yourusername/rookie-nl2sql.git

# 进入项目目录
cd rookie-nl2sql

# 查看所有分支
git branch -a
```

### 4. 创建虚拟环境

**推荐使用虚拟环境**，避免包冲突。

#### Windows
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

#### macOS / Linux
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

**验证**:
```bash
# 激活后，命令行前面应显示 (venv)
(venv) $ python --version
```

### 5. 安装依赖

```bash
# 确保虚拟环境已激活
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

**可能遇到的问题**:

<details>
<summary>安装 faiss-cpu 失败</summary>

如果遇到 faiss-cpu 安装问题：

```bash
# Windows 用户可能需要安装 Visual C++
# 下载并安装: https://visualstudio.microsoft.com/downloads/

# 或使用预编译版本
pip install faiss-cpu --no-cache-dir
```
</details>

<details>
<summary>安装速度慢</summary>

使用国内镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
</details>

## 配置 LLM API

### 选择 LLM 提供商

本课程支持三个 LLM 提供商，选择其中一个即可：

| 提供商 | 优势 | 价格 | 获取链接 |
|--------|------|------|----------|
| **DeepSeek** | 国内访问快，性价比高 | ¥1/百万 tokens | [platform.deepseek.com](https://platform.deepseek.com/) |
| **Qwen** | 阿里云生态，稳定 | ¥0.3-40/百万 tokens | [dashscope.aliyun.com](https://dashscope.aliyun.com/) |
| **OpenAI** | 性能强大 | $30/百万 tokens | [platform.openai.com](https://platform.openai.com/) |

**推荐国内用户使用 DeepSeek**。

### 获取 API Key

#### DeepSeek (推荐)

1. 访问 [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. 注册并登录
3. 点击 "API Keys" 创建新的 Key
4. 复制 API Key (格式: `sk-...`)

**首充优惠**: 新用户通常有免费额度

#### 通义千问 Qwen

1. 访问 [https://dashscope.aliyun.com/](https://dashscope.aliyun.com/)
2. 登录阿里云账号
3. 开通 DashScope 服务
4. 在 API-KEY 管理中创建 Key

#### OpenAI

1. 访问 [https://platform.openai.com/](https://platform.openai.com/)
2. 注册并登录
3. 进入 API Keys 页面
4. 创建新的 Secret Key

**注意**: 需要科学上网，且可能需要国外信用卡

### 配置环境变量

**1. 复制配置模板**

```bash
cp .env.example .env
```

**2. 编辑 `.env` 文件**

#### 使用 DeepSeek (推荐)

```bash
# .env 文件
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_MODEL=deepseek-chat
```

#### 使用 Qwen

```bash
# .env 文件
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QWEN_MODEL=qwen-plus
```

#### 使用 OpenAI

```bash
# .env 文件
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4
```

**3. 测试配置**

```bash
python configs/config.py
```

**预期输出**:
```
=== NL2SQL 配置测试 ===

LLM 配置:
  提供商: deepseek
  模型: deepseek-chat
  API Key 已设置: 是
  ✓ 配置加载成功
```

## 验证安装

运行 M0 验收测试，确保一切正常：

```bash
# 切换到 M0 分支
git checkout 00-scaffold

# 运行验收测试
python tests/test_m0_acceptance.py
```

**预期输出**:
```
======================================================================
M0 验收测试 - 项目脚手架与基线
======================================================================

✓ 测试用例 1 通过
✓ 测试用例 2 通过
✓ 测试用例 3 通过

通过: 3/3

🎉 恭喜! M0 验收测试全部通过!
```

如果看到这个输出，说明环境准备完毕！

## 推荐的开发工具

### VS Code 插件

推荐安装以下插件提升开发体验：

- **Python** (Microsoft): Python 语言支持
- **Pylance**: 类型检查和智能提示
- **GitLens**: Git 增强
- **Markdown All in One**: Markdown 编辑
- **Better Comments**: 注释高亮
- **YAML**: YAML 文件支持

### 其他工具

- **Postman**: API 测试（M12 模块会用到）
- **DBeaver**: 数据库查看（M2 模块会用到）

## 常见问题

### Q: M0 需要 API Key 吗？
A: **不需要**。M0 只是搭建框架，不调用 LLM。从 M1 开始才需要配置 API Key。

### Q: 我没有信用卡，怎么获取 API Key？
A: 使用 **DeepSeek** 或 **Qwen**，支持支付宝/微信支付，无需信用卡。

### Q: 虚拟环境激活后怎么退出？
A: 输入 `deactivate` 命令。

### Q: pip 安装很慢怎么办？
A: 使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: Windows 提示找不到 Python？
A: 确保安装时勾选了 "Add Python to PATH"，或手动添加到环境变量。

### Q: Mac M1/M2 芯片安装 faiss 失败？
A: 使用 conda 安装：
```bash
conda install -c conda-forge faiss-cpu
```

## 下一步

环境准备完成后：

👉 [开始学习 M0: 项目脚手架](/modules/m0/overview.md)

如果遇到问题：

👉 [查看详细的 LLM 配置指南](/guide/LLM_CONFIG_GUIDE.md)
👉 [GitHub Issues](https://github.com/yourusername/rookie-nl2sql/issues)
