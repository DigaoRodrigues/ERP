# Database & Migrations Agent

## Domain Overview

Expert in PostgreSQL database design, Alembic migrations, multi-tenant schema architecture, and query optimization for the ERP Multi-Tenant System.

## Core Responsibilities

- Multi-tenant database architecture (schema-per-workspace)
- Alembic migration management
- Query optimization and indexing
- Data integrity and constraints
- Backup and recovery strategies

---

## Multi-Tenant Architecture

### Schema-Per-Workspace Strategy

**Concept**: Each workspace gets its own PostgreSQL schema for complete data isolation.

```
Database: erp_db
├── Schema: public (shared tables)
│   ├── workspaces
│   ├── users
│   └── workspace_users
├── Schema: workspace_abc123 (tenant 1)
│   ├── products
│   ├── inventory
│   ├── sales
│   └── financial_records
└── Schema: workspace_xyz789 (tenant 2)
    ├── products
    ├── inventory
    ├── sales
    └── financial_records
```

### Benefits

1. **Complete Isolation**: No risk of data leakage between tenants
2. **Easy Backup**: Can backup/restore individual schemas
3. **Flexible Scaling**: Can move schemas to different databases
4. **Simple Queries**: No need for workspace_id in every query

### Implementation

```python
# app/core/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable connection pooling for multi-tenancy
    echo=settings.ENVIRONMENT == "development"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def set_workspace_schema(workspace_id: str):
    """Set the search_path to workspace schema."""
    schema_name = f"workspace_{workspace_id}"
    return f"SET search_path TO {schema_name}, public"
```

### Workspace Context Injection

```python
# app/core/workspace.py
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

async def get_current_workspace(
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
    db: Session = Depends(get_db)
) -> str:
    """Extract and validate workspace from request header."""
    # Validate workspace exists
    workspace = db.execute(
        "SELECT id FROM public.workspaces WHERE id = :id",
        {"id": workspace_id}
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Set schema for this request
    db.execute(f"SET search_path TO workspace_{workspace_id}, public")
    
    return workspace_id
```

---

## Database Schema Design

### Public Schema (Shared Tables)

```sql
-- Workspaces table
CREATE TABLE public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id UUID NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workspace users (many-to-many with roles)
CREATE TABLE public.workspace_users (
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'operator', 'viewer')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id)
);

-- Indexes
CREATE INDEX idx_workspaces_slug ON public.workspaces(slug);
CREATE INDEX idx_workspaces_owner ON public.workspaces(owner_id);
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_workspace_users_user ON public.workspace_users(user_id);
```

### Workspace Schema (Tenant Tables)

```sql
-- Products table (per workspace)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    acquisition_cost DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory table
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    location VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT positive_quantity CHECK (quantity >= 0)
);

-- Sales table
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    marketplace VARCHAR(50) NOT NULL CHECK (marketplace IN ('mercadolivre', 'shopee')),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    commission_rate DECIMAL(5, 4) NOT NULL,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    sale_date TIMESTAMP NOT NULL,
    payment_received_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial records table
CREATE TABLE financial_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(20) NOT NULL CHECK (type IN ('revenue', 'expense')),
    category VARCHAR(100),
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    transaction_date DATE NOT NULL,
    marketplace VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_marketplace ON sales(marketplace);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_financial_date ON financial_records(transaction_date);
CREATE INDEX idx_financial_type ON financial_records(type);
```

---

## Alembic Migrations

### Configuration

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.config import settings
from app.models.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="public"  # Store alembic_version in public schema
        )

        with context.begin_transaction():
            context.run_migrations()
```

### Creating Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "add products table"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### Migration Template for Workspace Schema

```python
"""add products table to workspace schema

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2026-05-19 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # This migration applies to ALL workspace schemas
    # Get all workspace schemas
    connection = op.get_bind()
    schemas = connection.execute(
        "SELECT 'workspace_' || id FROM public.workspaces"
    ).fetchall()
    
    for (schema,) in schemas:
        op.create_table(
            'products',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('sku', sa.String(100), nullable=False),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('acquisition_cost', sa.Numeric(10, 2), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('sku'),
            schema=schema
        )

def downgrade():
    connection = op.get_bind()
    schemas = connection.execute(
        "SELECT 'workspace_' || id FROM public.workspaces"
    ).fetchall()
    
    for (schema,) in schemas:
        op.drop_table('products', schema=schema)
```

---

## Query Optimization

### Use Indexes Strategically

```python
# ✅ GOOD: Query uses index
products = db.query(Product).filter(Product.sku == "ABC123").first()

# ❌ BAD: Full table scan
products = db.query(Product).filter(Product.name.like("%search%")).all()

# ✅ BETTER: Use full-text search
products = db.query(Product).filter(
    Product.name_tsvector.match("search")
).all()
```

### Avoid N+1 Queries

```python
# ❌ BAD: N+1 query problem
products = db.query(Product).all()
for product in products:
    inventory = product.inventory  # Separate query for each product!

# ✅ GOOD: Use joinedload
from sqlalchemy.orm import joinedload

products = db.query(Product).options(
    joinedload(Product.inventory)
).all()
```

### Pagination

```python
def get_products_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 50
) -> dict:
    """Get paginated products."""
    offset = (page - 1) * page_size
    
    query = db.query(Product)
    total = query.count()
    
    products = query.offset(offset).limit(page_size).all()
    
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
```

### Bulk Operations

```python
# ❌ BAD: Individual inserts
for item in items:
    db.add(Product(**item))
    db.commit()

# ✅ GOOD: Bulk insert
db.bulk_insert_mappings(Product, items)
db.commit()
```

---

## Data Integrity

### Constraints

```sql
-- Check constraints
ALTER TABLE inventory 
ADD CONSTRAINT positive_quantity CHECK (quantity >= 0);

-- Foreign key constraints with cascading
ALTER TABLE inventory
ADD CONSTRAINT fk_product
FOREIGN KEY (product_id) REFERENCES products(id)
ON DELETE CASCADE;

-- Unique constraints
ALTER TABLE products
ADD CONSTRAINT unique_sku UNIQUE (sku);
```

### Transactions

```python
from sqlalchemy.exc import IntegrityError

def transfer_inventory(
    db: Session,
    from_location: str,
    to_location: str,
    product_id: str,
    quantity: int
):
    """Transfer inventory between locations with transaction."""
    try:
        # Start transaction (implicit with session)
        
        # Deduct from source
        source = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.location == from_location
        ).with_for_update().first()
        
        if source.quantity < quantity:
            raise ValueError("Insufficient inventory")
        
        source.quantity -= quantity
        
        # Add to destination
        dest = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.location == to_location
        ).with_for_update().first()
        
        dest.quantity += quantity
        
        db.commit()
        
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {e}")
    except Exception as e:
        db.rollback()
        raise
```

---

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh - Daily backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="erp_db"

# Full database backup
pg_dump -U erp_user -h localhost $DB_NAME | gzip > "$BACKUP_DIR/full_backup_$DATE.sql.gz"

# Backup specific workspace schema
pg_dump -U erp_user -h localhost -n workspace_abc123 $DB_NAME | gzip > "$BACKUP_DIR/workspace_abc123_$DATE.sql.gz"

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### Point-in-Time Recovery

```bash
# Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'

# Restore to specific point in time
pg_restore -U erp_user -d erp_db -t "2026-05-19 10:00:00" backup.dump
```

---

## Performance Monitoring

### Query Analysis

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1s

-- Analyze query performance
EXPLAIN ANALYZE
SELECT p.*, i.quantity
FROM products p
JOIN inventory i ON p.id = i.product_id
WHERE p.category = 'electronics';

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Index Usage

```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname LIKE 'workspace_%'
ORDER BY idx_scan ASC;

-- Find missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname LIKE 'workspace_%'
  AND n_distinct > 100
  AND correlation < 0.1;
```

---

## Common Patterns

### Soft Deletes

```python
class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    sku = Column(String(100), unique=True, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None

# Query only active records
active_products = db.query(Product).filter(Product.deleted_at.is_(None)).all()
```

### Audit Trail

```python
class AuditMixin:
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID, ForeignKey("public.users.id"))
    updated_by = Column(UUID, ForeignKey("public.users.id"))

class Product(Base, AuditMixin):
    __tablename__ = "products"
    # ... other fields
```

---

## Related Agents

- **Multi-Tenancy Agent**: Workspace isolation strategies
- **API Design Agent**: Database session management in endpoints
- **Performance Agent**: Query optimization techniques

---

**Last Updated**: 2026-05-19  
**Version**: 1.0.0
