# ERP Multi-Tenant System

A multi-tenant SaaS ERP system designed for marketplace sellers (Shopee and Mercado Livre), built with FastAPI, Next.js, and PostgreSQL.

## 🚀 Features

- **Multi-tenant Architecture**: Complete data isolation using PostgreSQL schemas
- **Inventory Management**: Track stock across multiple marketplace channels
- **Pricing Calculator**: Prevent selling at a loss with intelligent pricing
- **Financial Control**: Separate revenue generated from revenue received
- **AI Integration**: Abstraction layer supporting Claude, GPT-4o, and Grok

## 🏗️ Architecture

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: Next.js 14 + TypeScript
- **Database**: PostgreSQL 15 with schema-per-workspace isolation
- **Authentication**: JWT with refresh tokens
- **Authorization**: RBAC (admin, operator, viewer)
- **Containerization**: Docker + Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development without Docker)
- Node.js 18+ (for local development without Docker)
- Git

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/DigaoRodrigues/ERP.git
cd ERP
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit backend/.env with your configuration
# Important: Change JWT_SECRET_KEY and database credentials
```

### 3. Start with Docker Compose

```bash
# Navigate to docker directory
cd docker

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### 5. Run Database Migrations (when implemented)

```bash
docker-compose exec backend alembic upgrade head
```

## 📁 Project Structure

```
ERP/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── auth/           # Authentication & authorization
│   │   ├── workspaces/     # Workspace management
│   │   ├── inventory/      # Inventory control
│   │   ├── pricing/        # Pricing calculator
│   │   ├── financial/      # Financial control
│   │   ├── ai/             # AI integration abstraction
│   │   ├── core/           # Shared utilities & config
│   │   └── main.py         # FastAPI application entry
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # Reusable components
│   │   ├── features/      # Feature-specific modules
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── package.json       # Node.js dependencies
│
├── docker/                 # Docker configuration
│   ├── docker-compose.yml # Service orchestration
│   ├── Dockerfile.backend # Backend container
│   ├── Dockerfile.frontend# Frontend container
│   └── init-db.sql        # Database initialization
│
├── AGENTS.md              # AI agent guidelines
└── README.md              # This file
```

## 🔧 Development

### Backend Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev
```

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## 🌿 Git Workflow

- `main` - Production-ready code
- `staging` - Pre-production testing
- `development` - Active development

```bash
# Create feature branch from development
git checkout development
git pull origin development
git checkout -b feature/your-feature-name

# After development, push and create PR to development
git push origin feature/your-feature-name
```

## 🚢 Deployment

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Add PostgreSQL plugin
3. Configure environment variables in Railway dashboard
4. Deploy backend and frontend as separate services
5. Run migrations: `railway run alembic upgrade head`

See [AGENTS.md](AGENTS.md) for detailed deployment instructions.

## 📚 Documentation

- [AGENTS.md](AGENTS.md) - Comprehensive project documentation for AI agents
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)
- [Ideia.txt](Ideia.txt) - Original project vision (Portuguese)

## 🔐 Security

- JWT authentication with refresh token rotation
- RBAC enforced at API level
- Schema-per-workspace data isolation
- Rate limiting per workspace
- Environment-based configuration

## 🤝 Contributing

This is currently a personal project, but contributions are welcome once the MVP is complete.

## 📝 License

Private - All rights reserved

## 👤 Author

**Rodrigo Martinez (DigaoRodrigues)**
- GitHub: [@DigaoRodrigues](https://github.com/DigaoRodrigues)

## 🗺️ Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Project structure
- [x] Docker configuration
- [x] Basic FastAPI setup
- [x] Next.js setup
- [ ] PostgreSQL multi-tenant setup
- [ ] JWT authentication

### Phase 2: Inventory Control
- [ ] Product SKU management
- [ ] Stock tracking
- [ ] Sales by channel
- [ ] Low stock alerts

### Phase 3: Pricing Module
- [ ] Cost calculator
- [ ] Marketplace commission handling
- [ ] Profit margin calculator

### Phase 4: Financial Control
- [ ] Revenue tracking
- [ ] Cash flow management
- [ ] P&L statements

### Phase 5: AI Features
- [ ] Invoice OCR
- [ ] Product description generation
- [ ] Pricing suggestions
- [ ] Sales forecasting

## 📞 Support

For questions or issues, please open an issue on GitHub.

---

**Status**: 🚧 In Development - Foundation Phase
