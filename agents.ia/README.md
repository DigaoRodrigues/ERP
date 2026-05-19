# AI Agents Knowledge Base

This directory contains specialized AI agent knowledge files for the ERP Multi-Tenant System. Each agent is an expert in a specific technical domain or business feature.

## Purpose

These agent files serve as:
- **Knowledge Repository**: Comprehensive documentation of system components
- **AI Assistant Guide**: Reference material for AI-powered development assistance
- **Onboarding Resource**: Help new developers understand the system
- **Best Practices Library**: Proven patterns and solutions

## Structure

```
agents.ia/
├── agent_index.md              # Master index and navigation guide
├── README.md                   # This file
│
├── Technical Domain Agents/
│   ├── docker_agent.md         # Containerization and deployment
│   ├── database_agent.md       # PostgreSQL and multi-tenancy
│   ├── auth_security_agent.md  # Authentication and security
│   ├── api_design_agent.md     # API patterns and design
│   ├── multitenancy_agent.md   # Workspace isolation
│   ├── nextjs_react_agent.md   # Frontend architecture
│   ├── ui_styling_agent.md     # UI/UX and Tailwind
│   ├── ai_integration_agent.md # AI provider abstraction
│   ├── cicd_agent.md           # CI/CD and deployment
│   ├── testing_agent.md        # Testing strategies
│   ├── performance_agent.md    # Optimization techniques
│   └── error_logging_agent.md  # Error handling and logging
│
└── Business Domain Agents/
    ├── inventory_agent.md      # Inventory management
    ├── pricing_agent.md        # Pricing calculations
    ├── financial_agent.md      # Financial control
    ├── mercadolivre_agent.md   # Mercado Livre integration
    ├── shopee_agent.md         # Shopee integration
    └── marketplace_sync_agent.md # Multi-marketplace sync
```

## How to Use

### For Developers

1. **Starting a new feature**: Consult `agent_index.md` to identify relevant agents
2. **Implementing**: Read the specific agent files for patterns and best practices
3. **Troubleshooting**: Check related agents for common issues and solutions

### For AI Assistants

1. **Understand context**: Read relevant agent files before making suggestions
2. **Follow patterns**: Use the code examples and patterns from agents
3. **Cross-reference**: Check related agents for integration points
4. **Stay consistent**: Maintain the architectural decisions documented in agents

### Quick Start Examples

**Implementing authentication:**
```
1. Read: auth_security_agent.md
2. Reference: api_design_agent.md (for endpoint structure)
3. Check: database_agent.md (for user table design)
```

**Adding inventory feature:**
```
1. Read: inventory_agent.md
2. Reference: database_agent.md (for schema design)
3. Check: multitenancy_agent.md (for workspace isolation)
4. Review: api_design_agent.md (for endpoint patterns)
```

**Deploying to production:**
```
1. Read: docker_agent.md
2. Reference: cicd_agent.md
3. Check: performance_agent.md (for optimization)
```

## Agent File Format

Each agent file follows this structure:

```markdown
# Agent Name

## Domain Overview
Brief description of the agent's expertise

## Core Responsibilities
- Responsibility 1
- Responsibility 2

## [Relevant Sections]
Detailed information, code examples, patterns

## Related Agents
Links to other relevant agents
```

## Maintenance

### Adding New Agents

1. Create new agent file in appropriate category
2. Follow the standard format
3. Update `agent_index.md` with new entry
4. Cross-reference with related agents
5. Commit with descriptive message

### Updating Agents

1. Keep agents synchronized with actual implementation
2. Update when architectural decisions change
3. Add new patterns as they emerge
4. Document lessons learned
5. Version control all changes

## Contributing

When adding or updating agent files:

- **Be specific**: Include actual code examples from the project
- **Be practical**: Focus on real-world usage, not theory
- **Be current**: Keep information up-to-date with the codebase
- **Be clear**: Write for both humans and AI assistants
- **Cross-reference**: Link to related agents

## Version History

- **v1.0.0** (2026-05-19): Initial agent knowledge base creation
  - Created 6 core agents (index, docker, database, auth, inventory, pricing)
  - Established agent file format and structure
  - Set up cross-referencing system

---

**Last Updated**: 2026-05-19  
**Maintained by**: Development Team
