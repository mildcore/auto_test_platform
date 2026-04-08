# 固件自动化测试平台

一个基于 Web 的自动化测试管理平台，用于管理测试用例、测试套件、测试计划和测试任务，支持异步任务执行和定时调度。

## 功能特性

- **测试用例管理**：创建、编辑、删除测试用例，支持分类和标签
- **测试套件管理**：将多个测试用例组合成测试套件，便于批量执行
- **测试计划管理**：制定测试计划，支持定时执行（Cron 表达式）
- **测试任务管理**：实时查看任务执行状态和结果，支持异步执行
- **用户认证**：JWT 认证机制，保障 API 安全
- **仪表板统计**：可视化展示测试执行统计信息

## 技术栈

### 后端

| 技术 | 说明 |
|------|------|
| [Flask](https://flask.palletsprojects.com/) | Python Web 框架 |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) | ORM 数据库操作 |
| [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/) | JWT 认证 |
| [Celery](https://docs.celeryproject.org/) | 异步任务队列 |
| [Redis](https://redis.io/) | 消息队列和缓存 |
| [MySQL](https://www.mysql.com/) | 主数据库 |
| [Alembic](https://alembic.sqlalchemy.org/) | 数据库迁移 |

### 前端

| 技术 | 说明 |
|------|------|
| [Vue 3](https://vuejs.org/) | 前端框架 |
| [Vite](https://vitejs.dev/) | 构建工具 |
| [Element Plus](https://element-plus.org/) | UI 组件库 |
| [Pinia](https://pinia.vuejs.org/) | 状态管理 |
| [Vue Router](https://router.vuejs.org/) | 路由管理 |
| [Axios](https://axios-http.com/) | HTTP 客户端 |

### 部署

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) - 容器化部署
- [Nginx](https://nginx.org/) - 前端服务器和反向代理
- [Gunicorn](https://gunicorn.org/) - WSGI HTTP 服务器

## 项目结构

```
.
├── backend/                 # 后端项目
│   ├── app/                # 应用代码
│   │   ├── api/            # API 路由
│   │   ├── models/         # 数据库模型
│   │   ├── services/       # 业务逻辑
│   │   ├── repositories/   # 数据访问层
│   │   └── celery_worker/  # Celery 任务
│   ├── migrations/         # 数据库迁移
│   ├── data/               # 数据文件
│   └── logs/               # 日志文件
├── frontend/               # 前端项目
│   ├── src/               # 源代码
│   │   ├── api/           # API 请求
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 公共组件
│   │   ├── stores/        # Pinia 状态
│   │   └── router/        # 路由配置
│   └── nginx.conf         # Nginx 配置
├── docker-compose.yml      # Docker Compose 配置
└── .env.example           # 环境变量示例
```

## 快速开始

### 方式一：Docker Compose 部署

1. 克隆项目并进入目录

```bash
cd auto_test_platform
```

2. 复制环境变量文件并修改配置

```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库密码和 JWT 密钥
```

3. 启动所有服务

```bash
docker compose build
docker compose up -d
docker compose run -e FLASK_ENV=production --rm backend flask db upgrade        # 初始数据库迁移
```

4. 访问应用

- 前端界面：http://localhost:5173
- 后端 API：http://localhost:5000

5. 查看日志

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f celery-worker
```

6. 停止服务

```bash
docker compose down
```

### 方式二：本地开发环境

#### 后端

1. 进入后端目录

```bash
cd backend
```

2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. 设置环境变量

```bash
export FLASK_ENV=development
export DATABASE_URL=sqlite:///data/dev.db
export JWT_SECRET_KEY=your-secret-key
```

4. 初始化数据库

```bash
flask db upgrade
```

5. 启动服务

```bash
# 开发服务器
python run.py

# 或使用 Flask CLI
flask run
```

后端服务将运行在 http://localhost:5000

#### 前端

1. 进入前端目录

```bash
cd frontend
```

2. 安装依赖

```bash
npm install #npm ci
```

3. 启动开发服务器

```bash
npm run dev
```

前端服务将运行在 http://localhost:5173

#### Celery（异步任务）

1. 确保 Redis 已启动

2. 启动 Celery Worker

```bash
cd backend
celery -A app.celery_worker worker -l info
```

3. 启动 Celery Beat（定时任务，可选）

```bash
celery -A app.celery_worker beat -l info
```

## 生产部署

使用生产环境配置部署：

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

生产环境包含：
- SSL 自动配置（Let's Encrypt）
- Traefik 反向代理
- 自动 HTTPS 重定向

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_ENV` | Flask 运行环境 | `production` |
| `DATABASE_URL` | 数据库连接 URL | SQLite/MySQL |
| `REDIS_URL` | Redis 连接 URL | `redis://redis:6379/0` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 必填（生产环境） |
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 | - |
| `MYSQL_USER` / `MYSQL_PASSWORD` | MySQL 用户/密码 | - |

## API 文档

API 前缀：`/api/v1`

主要接口：

| 接口 | 说明 |
|------|------|
| `POST /api/v1/auth/login` | 用户登录 |
| `GET /api/v1/dashboard/stats` | 获取统计数据 |
| `GET /api/v1/plans` | 测试计划列表 |
| `POST /api/v1/plans` | 创建测试计划 |
| `GET /api/v1/tasks` | 测试任务列表 |
| `POST /api/v1/tasks` | 创建测试任务 |
| `GET /api/v1/suites` | 测试套件列表 |
| `GET /api/v1/cases` | 测试用例列表 |

## 开发指南

### 数据库迁移

```bash
# 创建迁移
flask db migrate -m "migration message"

# 执行迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

### 添加 CLI 命令

在 `backend/app/cli.py` 中添加自定义命令。
