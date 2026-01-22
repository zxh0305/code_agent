# 智能GitHub代码开发协作平台

[English](README.md) | 简体中文

一个由AI驱动的智能GitHub代码开发协作平台，旨在简化代码开发、分析和PR管理流程。

---

## 📋 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [Docker Compose 部署](#docker-compose-部署)
  - [本地开发](#本地开发)
- [配置说明](#配置说明)
  - [必填配置](#必填配置)
  - [可选配置](#可选配置)
- [API接口文档](#api接口文档)
- [使用指南](#使用指南)
  - [GitHub OAuth 授权](#github-oauth-授权)
  - [代码分析功能](#代码分析功能)
  - [AI 功能使用](#ai-功能使用)
- [数据库迁移](#数据库迁移)
- [测试](#测试)
- [常见问题](#常见问题)
- [开源协议](#开源协议)

---

## 项目简介

本平台是一个集成 GitHub 和 AI 能力的智能代码协作工具，主要面向开发者和团队，提供以下核心价值：

- **自动化代码分析**：基于 AST 的深度代码结构解析和度量分析
- **AI 辅助开发**：集成多个 LLM 提供商，支持代码生成、修改、审核和 Bug 修复
- **GitHub 深度集成**：完整的 OAuth 授权、仓库管理、分支操作和 PR 生命周期管理
- **现代化架构**：基于 FastAPI 的异步后端，支持高并发和容器化部署

---

## 核心功能

### 1. GitHub 集成
- ✅ OAuth 2.0 授权认证
- ✅ 仓库列表获取和管理
- ✅ 分支列表和切换
- ✅ 仓库克隆和本地操作
- ✅ 文件内容读取和写入

### 2. 代码分析
- ✅ Python AST 语法解析
- ✅ 代码结构提取（类、函数、变量、导入）
- ✅ 代码度量计算（行数、复杂度、注释率）
- ✅ 单文件和整个仓库分析
- ✅ 代码上下文提取

### 3. AI 驱动操作
- ✅ 代码生成（支持多种编程语言）
- ✅ 代码修改和优化
- ✅ 代码审核和质量评估
- ✅ Bug 智能修复
- ✅ 自动生成文档
- ✅ PR 描述和提交信息生成

### 4. PR 管理
- ✅ 自动创建 Pull Request
- ✅ PR 详情查询
- ✅ PR 合并操作
- ✅ 评论和审核功能

### 5. 多 LLM 提供商支持
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ SiliconFlow (硅基流动)
- ✅ Qwen (千问)
- ✅ Zhipu (智谱)
- ✅ 本地 LLM (Ollama 等)

---

## 系统架构

```
智能GitHub代码开发协作平台
│
├── 前端 (Frontend)
│   ├── React + TypeScript
│   ├── Ant Design UI 组件库
│   └── Vite 构建工具
│
├── 后端 (Backend - FastAPI)
│   ├── app/
│   │   ├── api/                    # API 路由层
│   │   │   ├── github_routes.py     # GitHub 相关接口
│   │   │   ├── code_routes.py       # 代码分析接口
│   │   │   ├── pr_routes.py         # PR 管理接口
│   │   │   ├── llm_routes.py        # AI 大模型接口
│   │   │   └── settings_routes.py   # 设置管理接口
│   │   │
│   │   ├── core/                   # 核心配置和工具
│   │   │   ├── config.py            # 应用配置管理
│   │   │   ├── database.py          # 数据库连接池
│   │   │   ├── redis.py             # Redis 缓存客户端
│   │   │   ├── security.py          # JWT 认证和安全
│   │   │   ├── logging.py           # 结构化日志
│   │   │   ├── middleware.py        # 中间件（CORS、限流等）
│   │   │   └── validation.py        # 请求验证
│   │   │
│   │   ├── models/                 # 数据库模型 (SQLAlchemy)
│   │   │   ├── user.py             # 用户模型
│   │   │   ├── repository.py       # 仓库模型
│   │   │   ├── pull_request.py     # PR 模型
│   │   │   ├── code_analysis.py    # 代码分析模型
│   │   │   └── settings.py         # 系统设置模型
│   │   │
│   │   ├── services/               # 业务逻辑服务层
│   │   │   ├── github_service.py        # GitHub API 封装
│   │   │   ├── code_analysis_service.py # 代码分析核心逻辑
│   │   │   ├── pr_service.py            # PR 管理逻辑
│   │   │   ├── llm_service.py           # LLM 统一接口
│   │   │   └── settings_service.py       # 设置管理逻辑
│   │   │
│   │   └── main.py                # FastAPI 应用入口
│   │
│   ├── tests/                    # 测试套件
│   ├── scripts/                  # 数据库迁移和工具脚本
│   └── alembic/                  # 数据库迁移配置
│
├── 数据存储
│   ├── PostgreSQL (主数据库)
│   └── Redis (缓存和会话)
│
└── 外部服务
    ├── GitHub API
    ├── OpenAI API
    ├── SiliconFlow API
    ├── Qwen API
    └── Zhipu API
```

---

## 技术栈

### 后端技术
- **Web 框架**: FastAPI 0.104+ (异步高性能框架)
- **ASGI 服务器**: Uvicorn
- **数据库**: PostgreSQL 15 + SQLAlchemy 2.0 (异步 ORM)
- **缓存**: Redis 7
- **认证**: JWT (JSON Web Tokens)
- **日志**: Structlog (结构化日志)
- **数据库迁移**: Alembic

### AI 集成
- **OpenAI SDK**: 官方 Python SDK
- **代码分析**: Python AST (抽象语法树)
- **GitHub 集成**: PyGitHub + GitPython

### 前端技术
- **框架**: React 18 + TypeScript
- **UI 组件**: Ant Design 5.x
- **构建工具**: Vite 5.x
- **HTTP 客户端**: Fetch API

### 容器化
- **容器**: Docker
- **编排**: Docker Compose
- **镜像**: Alpine Linux (轻量级)

---

## 快速开始

### 环境要求

#### 必需软件
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+

#### 可选软件（本地开发）
- **Python**: 3.11+
- **Node.js**: 18+ (前端开发)
- **PostgreSQL**: 15+ (本地数据库)
- **Redis**: 7+ (本地缓存)

---

### Docker Compose 部署（推荐）

这是最简单、最快速的部署方式，适合生产环境和快速测试。

#### 步骤 1: 克隆项目

```bash
git clone https://github.com/zxh0305/code_agent.git
cd code_agent
```

#### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入您的配置
# Windows: notepad .env
# Linux/Mac: nano .env 或 vim .env
```

**必填配置项**（详见[配置说明](#配置说明)）：
- `GITHUB_CLIENT_ID` - GitHub OAuth App 客户端 ID
- `GITHUB_CLIENT_secret` - GitHub OAuth App 客户端密钥
- `DEFAULT_LLM_PROVIDER` - 默认 LLM 提供商
- 对应的 LLM API Key（如 `SILICONFLOW_API_KEY`）

#### 步骤 3: 启动所有服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

**启动的服务**：
- `code_agent_api` - 后端 API 服务 (端口 8082)
- `code_agent_db` - PostgreSQL 数据库 (端口 5432)
- `code_agent_redis` - Redis 缓存 (端口 6380)
- `code_agent_frontend` - 前端界面 (端口 3002)

#### 步骤 4: 验证部署

```bash
# 检查服务健康状态
curl http://localhost:8082/health

# 预期输出：
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "checks": {
#     "database": "healthy",
#     "redis": "healthy"
#   }
# }
```

#### 步骤 5: 访问应用

- **前端界面**: http://localhost:3002
- **API 文档 (Swagger)**: http://localhost:8082/docs
- **API 文档 (ReDoc)**: http://localhost:8082/redoc
- **健康检查**: http://localhost:8082/health

#### 常用 Docker Compose 命令

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（清空数据库）
docker-compose down -v

# 重启特定服务
docker-compose restart api

# 查看特定服务日志
docker-compose logs api --tail=100

# 进入容器调试
docker-compose exec api bash
```

---

### 本地开发

适合需要修改代码或调试的场景。

#### 步骤 1: 创建 Python 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 步骤 2: 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -e ".[dev]"
```

#### 步骤 3: 启动依赖服务

```bash
# 仅启动数据库和 Redis
docker-compose up -d db redis

# 验证服务状态
docker-compose ps
```

#### 步骤 4: 配置本地环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 修改数据库连接为本地
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/code_agent
# REDIS_URL=redis://localhost:6380/0
```

#### 步骤 5: 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或使用便捷脚本
./scripts/migrate.sh upgrade
```

#### 步骤 6: 启动后端服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8082

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8082 --workers 4
```

#### 步骤 7: 启动前端（可选）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 配置说明

### 必填配置

#### 1. GitHub OAuth 配置

**创建 GitHub OAuth App**：
1. 访问 https://github.com/settings/developers
2. 点击 "New OAuth App"
3. 填写应用信息：
   - **Application name**: 您的应用名称（如：Code Agent）
   - **Homepage URL**: `http://localhost:8082` (本地) 或您的域名
   - **Authorization callback URL**: `http://localhost:8082/api/v1/github/callback`
4. 创建后获取 `Client ID` 和 `Client Secret`

**环境变量配置**：
```env
GITHUB_CLIENT_ID=YOUR_CLIENT_ID
GITHUB_CLIENT_secret=YOUR_CLIENT_secret
GITHUB_REDIRECT_URI=http://localhost:8082/api/v1/github/callback
FRONTEND_URL=http://localhost:3002
```

#### 2. LLM 提供商配置

**选择一个提供商并配置**：

##### 选项 A: SiliconFlow（硅基流动）- 推荐
```env
DEFAULT_LLM_PROVIDER=siliconflow
SILICONFLOW_API_KEY=sk-your-siliconflow-api-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=Pro/zai-org/GLM-4.7
```

##### 选项 B: OpenAI
```env
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o
```

##### 选项 C: Qwen（千问）
```env
DEFAULT_LLM_PROVIDER=qwen
QWEN_API_KEY=your-qwen-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
```

##### 选项 D: Zhipu（智谱）
```env
DEFAULT_LLM_PROVIDER=zhipu
ZHIPU_API_KEY=your-zhipu-api-key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPU_MODEL=glm-4
```

##### 选项 E: 本地 LLM
```env
DEFAULT_LLM_PROVIDER=local
LOCAL_LLM_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=llama2
```

#### 3. 数据库配置

**Docker 部署**（默认配置，无需修改）：
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/code_agent
REDIS_URL=redis://redis:6380/0
```

**本地开发**：
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/code_agent
REDIS_URL=redis://localhost:6380/0
```

#### 4. JWT 安全配置

```env
JWT_secret_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

**生产环境必须修改 JWT 密钥**：
```bash
# 生成随机密钥
openssl rand -hex 32
```

---

### 可选配置

#### CORS 跨域设置
```env
CORS_ORIGINS=["http://localhost:3002","http://localhost:8082"]
```

#### 文件存储设置
```env
STORAGE_PATH=/tmp/code_agent
MAX_REPO_SIZE_MB=500
```

#### LLM 参数调优
```env
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
```

---

## API接口文档

### GitHub 集成接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|--------|
| `/api/v1/github/auth` | GET | 生成 OAuth 授权 URL | 无 |
| `/api/v1/github/callback` | GET | OAuth 回调处理 | 无 |
| `/api/v1/github/token` | POST | 交换授权码获取 Token | 无 |
| `/api/v1/github/user` | GET | 获取用户信息 | GitHub Token |
| `/api/v1/github/repos` | GET | 获取用户仓库列表 | GitHub Token |
| `/api/v1/github/repos/{owner}/{repo}` | GET | 获取仓库详情 | GitHub Token |
| `/api/v1/github/repos/{owner}/{repo}/branches` | GET | 获取分支列表 | GitHub Token |
| `/api/v1/github/repos/clone` | POST | 克隆仓库 | GitHub Token |
| `/api/v1/github/repos/analyze` | POST | 分析仓库代码 | GitHub Token |

### 代码分析接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|--------|
| `/api/v1/code/analyze` | POST | 分析源代码 | 无 |
| `/api/v1/code/analyze/file` | POST | 分析单个文件 | 无 |
| `/api/v1/code/analyze/repository` | POST | 分析整个仓库 | 无 |
| `/api/v1/code/context` | POST | 获取代码上下文 | 无 |
| `/api/v1/code/language` | GET | 检测编程语言 | 无 |

### PR 管理接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|--------|
| `/api/v1/pr/create` | POST | 创建新 PR | JWT |
| `/api/v1/pr/{owner}/{repo}/{pr_number}` | GET | 获取 PR 详情 | JWT |
| `/api/v1/pr/merge` | POST | 合并 PR | JWT |
| `/api/v1/pr/comment` | POST | 添加评论 | JWT |
| `/api/v1/pr/review` | POST | 创建审核 | JWT |

### AI 大模型接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|--------|
| `/api/v1/llm/generate` | POST | 生成代码 | 无 |
| `/api/v1/llm/modify` | POST | 修改现有代码 | 无 |
| `/api/v1/llm/review` | POST | 代码审核 | 无 |
| `/api/v1/llm/fix` | POST | Bug 修复 | 无 |
| `/api/v1/llm/docs` | POST | 生成文档 | 无 |
| `/api/v1/llm/pr-description` | POST | 生成 PR 描述 | 无 |
| `/api/v1/llm/commit-message` | POST | 生成提交信息 | 无 |

### 设置管理接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|--------|
| `/api/v1/settings` | GET | 获取所有设置 | 无 |
| `/api/v1/settings` | PUT | 更新设置 | 无 |

---

## 使用指南

### GitHub OAuth 授权

#### 1. 用户授权流程

```
用户点击"连接 GitHub"
    ↓
前端调用 GET /api/v1/github/auth
    ↓
后端生成 OAuth 授权 URL
    ↓
前端跳转到 GitHub 授权页面
    ↓
用户授权并确认
    ↓
GitHub 回调到 /api/v1/github/callback?code=xxx&state=xxx
    ↓
后端交换 code 获取 access_token
    ↓
后端重定向到前端并携带 token
    ↓
前端保存 token 到 localStorage
    ↓
后续请求携带 token 访问 GitHub API
```

#### 2. 使用授权后的功能

授权成功后，您可以：
- 查看您的 GitHub 仓库列表
- 选择仓库和分支
- 克隆仓库到本地
- 分析仓库代码
- 创建和管理 PR

---

### 代码分析功能

#### 1. 分析单个文件

**请求示例**：
```bash
curl -X POST http://localhost:8082/api/v1/code/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "source_code": "def hello():\n    print(\"Hello, World!\")",
    "language": "python"
  }'
```

**响应示例**：
```json
{
  "status": "success",
  "structure": {
    "classes": [],
    "functions": [
      {
        "name": "hello",
        "lineno": 1,
        "end_lineno": 2,
        "args": [],
        "defaults": [],
        "return_type": null,
        "docstring": null,
        "decorators": [],
        "is_async": false
      }
    ],
    "variables": [],
    "imports": []
  },
  "errors": [],
  "metrics": {
    "total_lines": 2,
    "code_lines": 2,
    "comment_lines": 0,
    "blank_lines": 0,
    "classes_count": 0,
    "functions_count": 1,
    "imports_count": 0
  }
}
```

#### 2. 分析整个仓库

**请求示例**：
```bash
curl -X POST http://localhost:8082/api/v1/code/analyze/repository \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repository",
    "extensions": [".py"]
  }'
```

#### 3. 使用前端分析代码

1. 访问 http://localhost:3002
2. 点击"连接 GitHub"并完成授权
3. 选择要分析的仓库和分支
4. 在"代码需求"输入框中描述您的分析需求
5. 点击"分析代码"按钮
6. 等待 AI 分析完成，查看结果

---

### AI 功能使用

#### 1. 代码生成

**请求示例**：
```bash
curl -X POST http://localhost:8082/api/v1/llm/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "创建一个计算斐波那契数列的函数",
    "language": "python",
    "provider": "siliconflow"
  }'
```

#### 2. 代码修改

**请求示例**：
```bash
curl -X POST http://localhost:8082/api/v1/llm/modify \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a + b",
    "instruction": "添加类型注解和文档字符串",
    "language": "python"
  }'
```

#### 3. 代码审核

**请求示例**：
```bash
curl -X POST http://localhost:8082/api/v1/llm/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a + b",
    "language": "python"
  }'
```

#### 4. Bug 修复

**请求示例**：
```bash
curl -X POST http://localhost:8082/api/v1/llm/fix \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def divide(a, b):\n    return a / b",
    "error_message": "ZeroDivisionError: division by zero",
    "language": "python"
  }'
```

---

## 数据库迁移

本项目使用 Alembic 进行数据库版本管理。

### 迁移命令

```bash
# 应用所有迁移（升级到最新版本）
./scripts/migrate.sh upgrade

# 回滚最近一次迁移
./scripts/migrate.sh downgrade -1

# 查看当前数据库版本
./scripts/migrate.sh current

# 查看迁移历史
./scripts/migrate.sh history

# 创建新迁移（基于模型变更自动生成）
./scripts/migrate.sh new "描述迁移内容"
```

### 手动迁移（使用 Alembic）

```bash
# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade <revision_id>

# 回滚到特定版本
alembic downgrade <revision_id>

# 查看当前版本
alembic current

# 查看历史版本
alembic history

# 生成新迁移
alembic revision --autogenerate -m "描述"
```

### 迁移文件位置

迁移文件位于 `alembic/versions/` 目录，命名格式：
```
<revision_id>_<description>.py
```

---

## 测试

### 运行测试套件

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_code_analysis.py -v

# 运行特定测试函数
pytest tests/test_code_analysis.py::test_analyze_python_code -v
```

### 生成覆盖率报告

```bash
# 生成 HTML 覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 查看报告
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### 测试覆盖率目标

- **单元测试覆盖率**: ≥ 80%
- **集成测试覆盖率**: ≥ 70%

---

## 常见问题

### 1. Docker 容器启动失败

**问题**：`docker-compose up -d` 后容器无法启动

**解决方案**：
```bash
# 查看容器日志
docker-compose logs api

# 检查端口占用
netstat -ano | findstr :8082

# 清理并重新启动
docker-compose down -v
docker-compose up -d
```

### 2. GitHub OAuth 授权失败

**问题**：授权后回调失败或 token 无效

**解决方案**：
- 检查 `GITHUB_REDIRECT_URI` 是否与 GitHub OAuth App 配置完全一致
- 确认 `FRONTEND_URL` 配置正确
- 检查浏览器控制台是否有 CORS 错误

### 3. LLM API 调用失败

**问题**：AI 功能返回 500 错误

**解决方案**：
- 检查 API Key 是否正确配置
- 确认 `DEFAULT_LLM_PROVIDER` 设置正确
- 查看后端日志：`docker-compose logs api --tail=100`
- 验证 API Key 是否有效（检查余额和权限）

### 4. 数据库连接失败

**问题**：`Database connection failed` 错误

**解决方案**：
```bash
# 检查数据库容器状态
docker-compose ps db

# 进入数据库容器
docker-compose exec db psql -U postgres -d code_agent

# 检查数据库连接字符串
echo $DATABASE_URL
```

### 5. 前端无法连接后端

**问题**：前端显示网络错误

**解决方案**：
- 检查 `CORS_ORIGINS` 配置是否包含前端地址
- 确认后端服务正常运行：`curl http://localhost:8082/health`
- 检查防火墙设置

### 6. 代码分析返回空结果

**问题**：分析仓库时没有返回任何文件

**解决方案**：
- 确认仓库包含支持的文件类型（.py, .js, .ts 等）
- 检查仓库克隆是否成功
- 查看后端日志了解详细错误

---

## 开源协议

MIT License

Copyright (c) 2024 Code Agent Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 联系方式

- **项目地址**: https://github.com/zxh0305/code_agent
- **问题反馈**: https://github.com/zxh0305/code_agent/issues
- **文档**: https://github.com/zxh0305/code_agent/wiki

---

**最后更新**: 2024-01-22
