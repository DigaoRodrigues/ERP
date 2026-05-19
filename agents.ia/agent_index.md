# AI Agents Index

This directory contains specialized AI agent knowledge files for the ERP Multi-Tenant System. Each agent focuses on a specific technical domain or business feature.

## How to Use This Index

When implementing a feature or fixing an issue, consult this index to identify which agent(s) to reference. Each agent file contains:
- Domain-specific knowledge
- Best practices and patterns
- Common pitfalls to avoid
- Code examples and templates
- Integration points with other agents

---

## Technical Domain Agents

### Infrastructure & DevOps

| Agent | File | Purpose | When to Consult |
|-------|------|---------|-----------------|
| **Docker & Containerization** | `docker_agent.md` | Container setup, multi-stage builds, optimization | Setting up containers, deployment issues, Docker configuration |
| **Database & Migrations** | `database_agent.md` | PostgreSQL, Alembic, multi-tenancy schema design | Database schema changes, migrations, query optimization |
| **CI/CD & Deployment** | `cicd_agent.md` | GitHub Actions, Railway deployment, environment management | Pipeline setup, deployment issues, environment configuration |

### Backend Architecture

| Agent | File | Purpose | When to Consult |
|-------|------|---------|-----------------|
| **Authentication & Security** | `auth_security_agent.md` | JWT, RBAC, security best practices | User authentication, authorization, security features |
| **API Design** | `api_design_agent.md` | FastAPI patterns, REST principles, error handling | Creating new endpoints, API structure, request/response design |
| **Multi-Tenancy** | `multitenancy_agent.md` | Workspace isolation, schema-per-tenant, context injection | Workspace features, tenant isolation, data separation |

### Frontend Architecture

| Agent | File | Purpose | When to Consult |
|-------|------|---------|-----------------|
| **Next.js & React** | `nextjs_react_agent.md` | App router, components, state management | Frontend features, routing, component design |
| **UI/UX & Styling** | `ui_styling_agent.md` | Tailwind CSS, responsive design, accessibility | Styling, layout, user interface components |

### AI Integration

| Agent | File | Purpose | When to Consult |
|-------|------|---------|-----------------|
| **AI Provider Abstraction** | `ai_integration_agent.md` | Multi-provider support, context injection, RAG | AI features, provider switching, prompt engineering |

---

## Business Domain Agents

### Core Business Features

| Agent | File | Purpose | When to Consult |
|-------|------|---------|-----------------|
| **Inventory Management** | `inventory_agent.md` | Stock control, SKU management, multi-channel inventory | Inventory features, stock tracking, product management |
| **Pricing Engine** | `pricing_agent.md` | Price calculation, commission handling, profit margins | Pricing features, cost calculations, margin analysis |
| **Financial Control** | `financial_agent.md` | Revenue tracking, cash flow, P&L statements | Financial features, reporting, payment tracking |

### Marketplace Integration

| Agent | File | Purpose | When to Consult |
|-------|------|---------|-----------------|
| **Mercado Livre Integration** | `mercadolivre_agent.md` | ML API, commission rates, payment flows | Mercado Livre features, ML-specific logic |
| **Shopee Integration** | `shopee_agent.md` | Shopee API, commission rates, payment flows | Shopee features, Shopee-specific logic |
| **Marketplace Sync** | `marketplace_sync_agent.md` | Cross-platform inventory, order sync, unified management | Multi-marketplace features, synchronization |

---

## Cross-Cutting Concerns

| Agent | File | Purpose | When to Consult |
|-------|------|---------|-----------------|
| **Testing Strategy** | `testing_agent.md` | Unit tests, integration tests, E2E tests, mocking | Writing tests, test coverage, testing patterns |
| **Performance Optimization** | `performance_agent.md` | Query optimization, caching, bundle size, monitoring | Performance issues, optimization, scalability |
| **Error Handling & Logging** | `error_logging_agent.md` | Error patterns, logging strategy, monitoring | Error handling, debugging, observability |

---

## Quick Reference Guide

### By Development Phase

**Planning & Design:**
1. `api_design_agent.md` - API structure
2. `database_agent.md` - Data model
3. `multitenancy_agent.md` - Tenant isolation

**Implementation:**
1. Relevant business domain agent
2. `auth_security_agent.md` - Security checks
3. `testing_agent.md` - Test strategy

**Deployment:**
1. `docker_agent.md` - Container setup
2. `cicd_agent.md` - Pipeline configuration
3. `performance_agent.md` - Optimization

### By Feature Type

**New Business Feature:**
1. Business domain agent (inventory/pricing/financial)
2. `api_design_agent.md`
3. `database_agent.md`
4. `nextjs_react_agent.md`
5. `testing_agent.md`

**Marketplace Integration:**
1. Marketplace-specific agent (ML/Shopee)
2. `marketplace_sync_agent.md`
3. `inventory_agent.md`
4. `api_design_agent.md`

**Security Feature:**
1. `auth_security_agent.md`
2. `api_design_agent.md`
3. `multitenancy_agent.md`

**Performance Issue:**
1. `performance_agent.md`
2. `database_agent.md`
3. `error_logging_agent.md`

---

## Agent Interaction Map

```
┌─────────────────────────────────────────────────────────────┐
│                    Business Domain Layer                     │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Inventory   │   Pricing    │  Financial   │  Marketplace   │
│    Agent     │    Agent     │    Agent     │  Sync Agent    │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       └──────────────┴──────────────┴────────────────┘
                      │
       ┌──────────────┴──────────────┐
       │                             │
┌──────▼───────┐            ┌────────▼────────┐
│  API Design  │            │  Multi-Tenancy  │
│    Agent     │            │     Agent       │
└──────┬───────┘            └────────┬────────┘
       │                             │
       └──────────────┬──────────────┘
                      │
       ┌──────────────┴──────────────┐
       │                             │
┌──────▼───────┐            ┌────────▼────────┐
│   Database   │            │  Auth/Security  │
│    Agent     │            │     Agent       │
└──────────────┘            └─────────────────┘
```

---

## Maintenance Notes

- **Keep agents focused**: Each agent should cover one domain thoroughly
- **Update regularly**: As features evolve, update relevant agents
- **Cross-reference**: Link related agents when concepts overlap
- **Examples matter**: Include real code examples from the project
- **Version control**: Track agent updates in git commits

---

**Last Updated**: 2026-05-19  
**Version**: 1.0.0
