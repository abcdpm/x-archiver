# x-archiver
定时下载自己X账号上点赞/收藏的推文内容，并将其保存到本地进行归档备份


```
x-archiver/
├── .gitignore               # 全局忽略配置
├── docker-compose.yml       # 统一编排前后端容器
├── README.md
├── LICENSE
│
├── backend/                 # 后端独立目录
│   ├── .gitignore
│   ├── .env.example         # 环境变量模板
│   ├── Dockerfile           # 后端容器构建
│   ├── requirements.txt     # 后端依赖
│   ├── tests/               # 单元测试
│   └── app/
│   │   ├── __init__.py
│   │   ├── main.py              # 极简入口：仅做应用初始化和路由挂载
│   │   ├── core/                # 核心配置
│   │   │   └── config.py        # 全局配置管理
│   │   ├── api/                 # 路由分发
│   │   │   └── routers.py       # API 路由，负责接收请求并调用 services
│   │   ├── services/            # 业务逻辑
│   │   │   ├── scraper.py       # 纯粹的网页抓取逻辑
│   │   │   └── downloader.py    # 纯粹的文件/媒体下载逻辑
│   │   ├── models/              # 数据库模型
│   │   │   └── archive.py       # 数据库 ORM 表结构
│   │   └── database.py          # 数据库连接池/初始化
│
└── frontend/                # 前端独立目录
    ├── .gitignore
    ├── .env.example
    ├── Dockerfile           # 前端容器构建
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── App.vue
        ├── api/             # 接口请求封装
        ├── assets/          # 静态资源
        ├── components/      # 公共组件
        ├── views/           # 页面组件
        ├── stores/          # 状态管理
        └── style.css
```