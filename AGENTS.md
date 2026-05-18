# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

This is a **multi-tenant SaaS ERP system** designed for marketplace sellers, specifically targeting vendors on Shopee and Mercado Livre (Brazilian marketplaces). The project is being developed as a personal tool that will evolve into a commercial product with subscription-based monetization.

### Business Context

- **Primary User**: Marketplace sellers managing inventory and sales across multiple platforms
- **Initial Scope**: Personal use by the developer (a marketplace seller)
- **Future Vision**: Commercial SaaS product with tiered pricing plans
- **Core Problem**: Managing inventory, pricing, and finances across multiple marketplace channels

### Technology Stack

**Backend:**
- Python with FastAPI framework
- PostgreSQL database with Alembic for migrations
- Multi-tenant architecture using PostgreSQL schemas (one schema per workspace)
- JWT-based authentication with refresh tokens (python-jose or authlib)
- RBAC (Role-Based Access Control) with admin, operator, and viewer roles

**Frontend:**
- Next.js with TypeScript
- Modern React patterns and best practices

**Infrastructure:**
- Docker containerization from day one
- CI/CD with GitHub Actions
- Initial hosting on Railway
- Separate environments: dev, staging, production

**AI Integration:**
- Abstraction layer supporting multiple AI providers:
  - Claude (Anthropic)
  - GPT-4o (OpenAI)
  - Grok (xAI)
- Phase 1: Direct context injection in prompts
- Phase 2: RAG implementation using pgvector in PostgreSQL
- Support for image processing (invoice OCR, product description generation)

## Architecture Principles

### Multi-Tenancy

- **Isolation Strategy**: PostgreSQL schema-per-workspace
- Each client workspace is completely isolated at the database level
- Shared application code with tenant context injection
- Rate limiting per workspace to prevent resource abuse

### Security

- JWT tokens with refresh token rotation
- RBAC enforced at API level
- Developer has background in security and infrastructure
- Security-first approach from initial implementation

### Scalability

- Designed to scale from single user to commercial product
- Clean separation of concerns
- Domain-driven design approach
- Stateless API design

## Project Structure (Planned)

```
/backend
  /app
    /auth          # Authentication & authorization
    /workspaces    # Workspace management
    /inventory     # Inventory control module
    /pricing       # Pricing calculation module
    /financial     # Financial control module
    /ai            # AI integration abstraction layer
    /core          # Shared utilities, database, config
  /alembic         # Database migrations
  /tests

/frontend
  /src
    /app           # Next.js app directory
    /components    # Reusable components
    /features      # Feature-specific modules
    /lib           # Utilities and helpers
    /types         # TypeScript type definitions

/docker
  docker-compose.yml
  Dockerfile.backend
  Dockerfile.frontend

/.github
  /workflows       # CI/CD pipelines
```

## Development Roadmap

### Phase 1: Foundation (Current Priority)
1. Project structure setup
2. Docker configuration
3. PostgreSQL with multi-tenant schema support
4. JWT authentication system
5. Basic workspace management

### Phase 2: Inventory Control
- Product SKU management
- Stock entry tracking with acquisition costs
- Sales tracking by channel (Mercado Livre and Shopee)
- Current stock levels per SKU
- Low stock alerts
- **Key Feature**: Unified inventory across marketplaces (same product can be listed on both platforms)

### Phase 3: Pricing Module
- Minimum viable price calculator considering:
  - Acquisition cost
  - Marketplace commission (different rates for ML and Shopee by category)
  - Shipping costs (when absorbed by seller)
  - Desired profit margin
- **Goal**: Prevent selling at a loss

### Phase 4: Financial Control
- Revenue tracking: generated vs. received (marketplaces have payment delays)
- Cash flow consolidation
- Simple P&L (Profit & Loss) statement by period
- Channel-specific financial reporting

### Phase 5: AI Features
- Invoice data extraction from images
- Product description generation from photos
- Intelligent pricing suggestions
- Sales forecasting

## Development Guidelines

### Code Quality
- Write clean, maintainable code
- Follow Python PEP 8 style guide
- Use TypeScript strict mode
- Implement comprehensive error handling
- Add logging for debugging and monitoring

### Testing
- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests for critical user flows

### Documentation
- API documentation via FastAPI's automatic Swagger/OpenAPI
- Code comments for complex logic
- README files for each major module
- Keep this AGENTS.md updated as the project evolves

### DevOps Practices
- Automated deployment on push to main branch
- Environment-specific configurations via environment variables
- Docker image versioning for rollback capability
- Centralized logging (Grafana Loki or Papertrail)
- Automated PostgreSQL backups with pg_dump

### Cost Optimization
- Start with minimal or zero-cost infrastructure
- Optimize database queries
- Implement caching where appropriate
- Monitor resource usage per workspace

## Domain-Specific Knowledge

### Marketplace Integration
- **Mercado Livre (ML)**: Brazilian marketplace with category-specific commission rates
- **Shopee**: Asian marketplace expanding in Brazil, different commission structure
- Both platforms have payment delays (revenue generated ≠ revenue received)
- Products can be listed simultaneously on both platforms

### Multi-Tenant Considerations
- Each workspace represents a different seller/business
- Complete data isolation is critical
- Workspace-level rate limiting prevents abuse
- Future monetization will be workspace-based (per-workspace subscription)

### AI Integration Strategy
- Provider-agnostic design allows switching between Claude, GPT-4o, and Grok
- Context injection pattern: fetch relevant workspace data before each AI call
- Future RAG implementation will use pgvector for semantic search
- Image processing capabilities for invoice OCR and product descriptions

## Getting Started (Once Implemented)

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Local Development Setup
```bash
# Clone repository
git clone <repository-url>
cd ERP

# Start services with Docker Compose
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Environment Variables
Key environment variables to configure:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret for JWT token signing
- `AI_PROVIDER`: claude | openai | xai
- `AI_API_KEY`: API key for selected AI provider
- `ENVIRONMENT`: dev | staging | production

## Important Notes for AI Agents

1. **Multi-Tenancy is Critical**: Always ensure workspace context is properly injected in all operations
2. **Security First**: Never bypass authentication or authorization checks
3. **Marketplace-Specific Logic**: ML and Shopee have different commission structures and payment flows
4. **Inventory Synchronization**: Stock must be unified across marketplaces to prevent overselling
5. **AI Provider Abstraction**: Never hardcode AI provider logic; always use the abstraction layer
6. **Cost Awareness**: This is a bootstrapped project; optimize for minimal infrastructure costs
7. **Iterative Development**: Start with MVP features and iterate based on real usage

## Current Status

**Project Phase**: Initial Planning / Foundation Setup

The project is currently in the ideation and planning phase. The core architecture has been defined, but implementation has not yet begun. The next steps are to:
1. Set up the project structure
2. Configure Docker environment
3. Implement multi-tenant database architecture
4. Build authentication system

Refer to `Ideia.txt` for the original project vision in Portuguese.
