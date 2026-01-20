# 智能GitHub代码开发协作平台

[English](README.md) | 简体中文

一个由AI驱动的智能GitHub代码开发协作平台，旨在简化代码开发、分析和PR管理流程。

## 功能特性

- **GitHub集成**: OAuth授权认证、仓库管理、分支操作
- **代码分析**: AST语法解析、代码结构提取、度量指标计算
- **AI驱动操作**: 代码生成、修改、审核、Bug修复
- **PR管理**: 自动化PR创建、审核和生命周期管理

## 系统架构

```
├── app/
│   ├── api/              # API路由处理
│   │   ├── github_routes.py    # GitHub相关接口
│   │   ├── code_routes.py      # 代码分析接口
│   │   ├── pr_routes.py        # PR管理接口
│   │   └── llm_routes.py       # AI大模型接口
│   ├── core/             # 核心配置和工具
│   │   ├── config.py           # 应用配置
│   │   ├── database.py         # 数据库连接
│   │   ├── redis.py            # Redis缓存
│   │   └── security.py         # 安全认证
│   ├── models/           # 数据库模型
│   │   ├── user.py             # 用户模型
│   │   ├── repository.py       # 仓库模型
│   │   ├── pull_request.py     # PR模型
│   │   └── code_analysis.py    # 代码分析模型
│   ├── services/         # 业务逻辑服务
│   │   ├── github_service.py        # GitHub服务
│   │   ├── code_analysis_service.py # 代码分析服务
│   │   ├── pr_service.py            # PR管理服务
│   │   └── llm_service.py           # AI大模型服务
│   └── main.py           # FastAPI应用入口
├── tests/                # 测试文件
├── scripts/              # 数据库和工具脚本
├── config/               # 配置文件
└── docs/                 # 文档
```

## 快速开始

### 环境要求

- Python 3.11+
- Docker 和 Docker Compose
- GitHub OAuth App 凭证
- OpenAI API密钥（可选，用于AI功能）

### 使用 Docker Compose 部署

1. 克隆仓库：
```bash
git clone https://github.com/zxh0305/code_agent.git
cd code_agent
```

2. 复制并配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问API文档：
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### 本地开发

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows系统使用: venv\Scripts\activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # 安装开发依赖
```

3. 启动依赖服务（PostgreSQL, Redis）：
```bash
docker-compose up -d db redis
```

4. 运行数据库迁移：
```bash
# 应用所有数据库迁移
./scripts/migrate.sh upgrade

# 或使用alembic命令
alembic upgrade head
```

5. 运行应用：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## 数据库迁移

本项目使用Alembic进行数据库迁移管理。提供了便捷的迁移脚本：

```bash
# 应用所有迁移
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

## API接口

### GitHub集成
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/github/auth` | GET | 生成OAuth授权URL |
| `/api/v1/github/callback` | GET | OAuth回调处理 |
| `/api/v1/github/repos` | GET | 获取用户仓库列表 |
| `/api/v1/github/repos/clone` | POST | 克隆仓库 |

### 代码分析
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/code/analyze` | POST | 分析源代码 |
| `/api/v1/code/analyze/file` | POST | 分析单个文件 |
| `/api/v1/code/analyze/repository` | POST | 分析整个仓库 |

### PR管理
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/pr/create` | POST | 创建新PR |
| `/api/v1/pr/{owner}/{repo}/{pr_number}` | GET | 获取PR详情 |
| `/api/v1/pr/merge` | POST | 合并PR |
| `/api/v1/pr/comment` | POST | 添加评论 |
| `/api/v1/pr/review` | POST | 创建审核 |

### AI大模型操作
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/llm/generate` | POST | 生成代码 |
| `/api/v1/llm/modify` | POST | 修改现有代码 |
| `/api/v1/llm/review` | POST | 代码审核 |
| `/api/v1/llm/fix` | POST | Bug修复 |
| `/api/v1/llm/docs` | POST | 生成文档 |
| `/api/v1/llm/pr-description` | POST | 生成PR描述 |
| `/api/v1/llm/commit-message` | POST | 生成提交信息 |

## 配置说明

关键环境变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL连接URL | 必填 |
| `REDIS_URL` | Redis连接URL | 必填 |
| `GITHUB_CLIENT_ID` | GitHub OAuth App客户端ID | 必填 |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App客户端密钥 | 必填 |
| `OPENAI_API_KEY` | OpenAI API密钥 | 可选 |
| `JWT_SECRET_KEY` | JWT签名密钥 | 必填 |
| `LOCAL_LLM_URL` | 本地LLM服务地址 | 可选 |
| `LOCAL_LLM_MODEL` | 本地LLM模型名称 | 可选 |

## 测试

运行测试：
```bash
pytest tests/ -v
```

生成覆盖率报告：
```bash
pytest tests/ --cov=app --cov-report=html
```

## 技术栈

- **后端框架**: FastAPI + Uvicorn
- **数据库**: PostgreSQL + SQLAlchemy (异步)
- **缓存**: Redis
- **AI集成**: OpenAI API + 本地LLM支持
- **代码分析**: Python AST
- **GitHub集成**: PyGitHub + GitPython
- **容器化**: Docker + Docker Compose

## 开源协议

MIT License
