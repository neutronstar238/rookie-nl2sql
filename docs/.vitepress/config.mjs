import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "NL2SQL LangGraph 实战课程",
  description: "基于 LangGraph 构建生产级 NL2SQL 系统",
  lang: 'zh-CN',

  themeConfig: {
    logo: '/logo.svg',

    nav: [
      { text: '首页', link: '/' },
      { text: '课程指南', link: '/guide/introduction' },
      { text: '模块列表', link: '/modules/' },
      { text: 'GitHub', link: 'https://github.com/yourusername/rookie-nl2sql' }
    ],

    sidebar: {
      '/guide/': [
        {
          text: '开始',
          items: [
            { text: '课程介绍', link: '/guide/introduction' },
            { text: '课程目标', link: '/guide/objectives' },
            { text: 'NL2SQL 系统概述', link: '/guide/nl2sql-overview' },
            { text: '技术栈', link: '/guide/tech-stack' },
            { text: '环境准备', link: '/guide/setup' }
          ]
        }
      ],
      '/modules/': [
        {
          text: 'M0 - 项目脚手架',
          items: [
            { text: '模块概述', link: '/modules/m0/overview' },
            { text: '项目结构设计', link: '/modules/m0/project-structure' },
            { text: '配置系统', link: '/modules/m0/configuration' },
            { text: 'LangGraph 基础', link: '/modules/m0/langgraph-basics' },
            { text: '实践任务', link: '/modules/m0/tasks' }
          ]
        },
        {
          text: 'M1 - 提示词工程',
          items: [
            { text: '模块概述', link: '/modules/m1/overview' },
            { text: '提示词工程详解', link: '/modules/m1/prompt-engineering' },
            { text: 'LLM Client 设计', link: '/modules/m1/llm-client' },
            { text: '实践任务', link: '/modules/m1/tasks' }
          ]
        },
        {
          text: 'M2 - Function Call',
          items: [
            { text: '模块概述', link: '/modules/m2/overview' },
            { text: 'Function Call 详解', link: '/modules/m2/function-call' }
          ]
        },
        {
          text: 'M3 - Schema 感知',
          items: [
            { text: '模块概述', link: '/modules/m3/overview' }
          ]
        },
        {
          text: 'M4 - SQL 校验',
          items: [
            { text: '模块概述', link: '/modules/m4/overview' }
          ]
        },
        {
          text: 'M5 - 执行沙箱',
          items: [
            { text: '模块概述', link: '/modules/m5/overview' }
          ]
        },
        {
          text: 'M6 - RAG 增强',
          items: [
            { text: '模块概述', link: '/modules/m6/overview' }
          ]
        },
        {
          text: 'M7 - 多轮对话',
          items: [
            { text: '模块概述', link: '/modules/m7/overview' }
          ]
        },
        {
          text: 'M8 - 多表联结',
          items: [
            { text: '模块概述', link: '/modules/m8/overview' }
          ]
        },
        {
          text: 'M9 - 答案生成',
          items: [
            { text: '模块概述', link: '/modules/m9/overview' }
          ]
        },
        {
          text: 'M10 - 系统评测',
          items: [
            { text: '模块概述', link: '/modules/m10/overview' }
          ]
        },
        {
          text: 'M11 - 可观测性',
          items: [
            { text: '模块概述', link: '/modules/m11/overview' }
          ]
        },
        {
          text: 'M12 - API & UI',
          items: [
            { text: '模块概述', link: '/modules/m12/overview' }
          ]
        },
        {
          text: 'M13 - 部署',
          items: [
            { text: '模块概述', link: '/modules/m13/overview' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/yourusername/rookie-nl2sql' }
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present'
    },

    search: {
      provider: 'local'
    },

    outline: {
      level: [2, 3],
      label: '目录'
    },

    docFooter: {
      prev: '上一页',
      next: '下一页'
    },

    lastUpdated: {
      text: '最后更新于',
      formatOptions: {
        dateStyle: 'short',
        timeStyle: 'short'
      }
    }
  }
})
