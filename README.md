# GitHub Code Collaboration Platform

English | [简体中文](README_CN.md)

A smart GitHub code development collaboration platform powered by AI, designed to streamline code development, analysis, and PR management.

## Features

- **GitHub Integration**: OAuth authentication, repository management, branch operations
- **Code Analysis**: AST parsing, structure extraction, metrics calculation
- **AI-Powered Operations**: Code generation, modification, review, bug fixing
- **PR Management**: Automated PR creation, review, and lifecycle management

## Architecture

```
├── app/
│   ├── api/              # API route handlers
│   │   ├── github_routes.py
│   │   ├── code_routes.py
│   │   ├── pr_routes.py
│   │   └── llm_routes.py
│   ├── core/             # Core configuration and utilities
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   └── security.py
│   ├── models/           # Database models
│   │   ├── user.py
│   │   ├── repository.py
│   │   ├── pull_request.py
│   │   └── code_analysis.py
│   ├── services/         # Business logic services
│   │   ├── github_service.py
│   │   ├── code_analysis_service.py
│   │   ├── pr_service.py
│   │   └── llm_service.py
│   └── main.py           # FastAPI application entry point
├── tests/                # Test files
├── scripts/              # Database and utility scripts
├── config/               # Configuration files
└── docs/                 # Documentation
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- GitHub OAuth App credentials
- OpenAI API key (optional, for AI features)

### Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/your-org/code-agent.git
cd code-agent
```

2. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the API documentation:
- Swagger UI: http://localhost:8082/docs
- ReDoc: http://localhost:8082/redoc
- Frontend: http://localhost:3002

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # For development dependencies
```

3. Start required services (PostgreSQL, Redis):
```bash
docker-compose up -d db redis
```

4. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8082
```

## API Endpoints

### GitHub Integration
- `GET /api/v1/github/auth` - Generate OAuth authorization URL
- `GET /api/v1/github/callback` - OAuth callback handler
- `GET /api/v1/github/repos` - List user repositories
- `POST /api/v1/github/repos/clone` - Clone a repository

### Code Analysis
- `POST /api/v1/code/analyze` - Analyze source code
- `POST /api/v1/code/analyze/file` - Analyze a file
- `POST /api/v1/code/analyze/repository` - Analyze entire repository

### Pull Requests
- `POST /api/v1/pr/create` - Create a new PR
- `GET /api/v1/pr/{owner}/{repo}/{pr_number}` - Get PR details
- `POST /api/v1/pr/merge` - Merge a PR

### LLM Operations
- `POST /api/v1/llm/generate` - Generate code
- `POST /api/v1/llm/modify` - Modify existing code
- `POST /api/v1/llm/review` - Review code
- `POST /api/v1/llm/fix` - Fix bugs

## Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `REDIS_URL` | Redis connection URL | Required |
| `GITHUB_CLIENT_ID` | GitHub OAuth App client ID | Required |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App client secret | Required |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `JWT_SECRET_KEY` | JWT signing key | Required |

## Testing

Run tests with pytest:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## License

MIT License
