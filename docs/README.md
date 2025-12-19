# NL2SQL LangGraph 课程文档

本目录包含完整的 NL2SQL LangGraph 实战课程文档，使用 VitePress 构建。

## 快速开始

### 安装依赖

```bash
cd docs
npm install
```

### 本地开发

启动开发服务器（支持热更新）：

```bash
npm run docs:dev
```

访问 http://localhost:5173 查看文档。

### 构建生产版本

```bash
npm run docs:build
```

构建产物在 `docs/.vitepress/dist` 目录。

### 预览生产构建

```bash
npm run docs:preview
```

## 文档结构

```
docs/
├── .vitepress/
│   └── config.mjs          # VitePress 配置
├── guide/                  # 课程指南
│   ├── introduction.md     # 课程介绍
│   ├── nl2sql-overview.md  # NL2SQL 系统概述
│   └── setup.md            # 环境准备
├── modules/                # 模块文档
│   ├── index.md            # 模块列表
│   └── m0/                 # M0 模块文档
│       ├── overview.md     # 模块概述
│       ├── project-structure.md  # 项目结构
│       └── tasks.md        # 实践任务
├── index.md                # 首页
├── package.json
└── README.md               # 本文件
```

## 编写文档

### 添加新页面

1. 在对应目录创建 `.md` 文件
2. 在 `.vitepress/config.mjs` 中添加导航/侧边栏配置

### Markdown 语法

支持标准 Markdown 和 VitePress 扩展语法：

#### 提示框

```markdown
::: tip 提示
这是一个提示
:::

::: warning 警告
这是一个警告
:::

::: danger 危险
这是一个危险提示
:::

::: details 点击展开
这是可折叠的内容
:::
```

#### 代码块

````markdown
```python
def hello():
    print("Hello, World!")
```
````

#### Mermaid 图表

````markdown
```mermaid
graph LR
    A[开始] --> B[处理]
    B --> C[结束]
```
````

## 部署

### GitHub Pages

1. 构建文档：
```bash
npm run docs:build
```

2. 部署到 GitHub Pages：
```bash
# 方式1: 使用 gh-pages 分支
npm install -g gh-pages
gh-pages -d docs/.vitepress/dist

# 方式2: 使用 GitHub Actions
# 参考 .github/workflows/deploy-docs.yml
```

### 其他平台

- **Vercel**: 导入项目，设置构建命令为 `cd docs && npm run docs:build`
- **Netlify**: 同上
- **自建服务器**: 将 `docs/.vitepress/dist` 目录部署到 Nginx/Apache

## 贡献文档

欢迎贡献文档！

1. Fork 项目
2. 创建分支：`git checkout -b docs/your-feature`
3. 编写文档
4. 提交 PR

### 文档规范

- 使用中文编写
- 代码示例要完整可运行
- 添加必要的注释和说明
- 保持文档结构清晰

## License

MIT
