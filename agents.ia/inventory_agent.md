# Inventory Management Agent

## Domain Overview

Expert in inventory control, stock management, SKU tracking, and multi-channel inventory synchronization for marketplace sellers.

## Core Responsibilities

- Product SKU management
- Stock level tracking and updates
- Multi-marketplace inventory synchronization
- Low stock alerts
- Inventory valuation (FIFO/LIFO)

---

## Business Context

### Problem Statement

Marketplace sellers need to:
- Track inventory across multiple sales channels (Mercado Livre, Shopee)
- Prevent overselling (same product listed on multiple platforms)
- Monitor stock levels and get alerts
- Track acquisition costs for profit calculation
- Maintain accurate inventory records

### Solution Approach

**Unified Inventory**: Single source of truth for stock levels
**Real-time Sync**: Update inventory across all channels when sale occurs
**Cost Tracking**: Record acquisition cost for each stock entry

---

## Data Model

### Products Table

```python
from sqlalchemy import Column, String, Text, Numeric, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Product(Base):
    """Product master data."""
    __tablename__ = "products"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)
    
    # Cost tracking
    acquisition_cost = Column(Numeric(10, 2), nullable=False)
    
    # Marketplace identifiers
    mercadolivre_id = Column(String(100), unique=True)
    shopee_id = Column(String(100), unique=True)
    
    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    sales = relationship("Sale", back_populates="product")
```

### Inventory Table

```python
class Inventory(Base):
    """Current inventory levels."""
    __tablename__ = "inventory"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID, ForeignKey("products.id"), nullable=False, unique=True)
    
    # Stock levels
    quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)  # Pending orders
    available_quantity = Column(Integer, nullable=False, default=0)  # quantity - reserved
    
    # Location tracking
    location = Column(String(100))
    
    # Alerts
    low_stock_threshold = Column(Integer, default=10)
    
    # Metadata
    last_updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="inventory")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='positive_quantity'),
        CheckConstraint('reserved_quantity >= 0', name='positive_reserved'),
        CheckConstraint('available_quantity >= 0', name='positive_available'),
    )
```

### Stock Movements Table (Audit Trail)

```python
class StockMovement(Base):
    """Track all inventory changes."""
    __tablename__ = "stock_movements"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID, ForeignKey("products.id"), nullable=False)
    
    # Movement details
    movement_type = Column(String(20), nullable=False)  # purchase, sale, adjustment, return
    quantity = Column(Integer, nullable=False)
    
    # Cost tracking
    unit_cost = Column(Numeric(10, 2))
    
    # Reference
    reference_type = Column(String(50))  # sale_id, purchase_order_id, etc.
    reference_id = Column(UUID)
    
    # Metadata
    notes = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    created_by = Column(UUID, ForeignKey("public.users.id"))
```

---

## Core Operations

### 1. Add Stock (Purchase/Restock)

```python
from sqlalchemy.orm import Session
from decimal import Decimal

def add_stock(
    db: Session,
    product_id: str,
    quantity: int,
    unit_cost: Decimal,
    notes: str = None,
    user_id: str = None
) -> Inventory:
    """Add stock to inventory."""
    
    # Get or create inventory record
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()
    
    if not inventory:
        inventory = Inventory(
            product_id=product_id,
            quantity=0,
            reserved_quantity=0,
            available_quantity=0
        )
        db.add(inventory)
    
    # Update quantities
    inventory.quantity += quantity
    inventory.available_quantity = inventory.quantity - inventory.reserved_quantity
    
    # Record movement
    movement = StockMovement(
        product_id=product_id,
        movement_type="purchase",
        quantity=quantity,
        unit_cost=unit_cost,
        notes=notes,
        created_by=user_id
    )
    db.add(movement)
    
    # Update product acquisition cost (weighted average)
    product = db.query(Product).filter(Product.id == product_id).first()
    total_cost = (product.acquisition_cost * (inventory.quantity - quantity)) + (unit_cost * quantity)
    product.acquisition_cost = total_cost / inventory.quantity
    
    db.commit()
    db.refresh(inventory)
    
    return inventory
```

### 2. Reserve Stock (Order Placed)

```python
def reserve_stock(
    db: Session,
    product_id: str,
    quantity: int,
    reference_id: str = None
) -> bool:
    """Reserve stock for pending order."""
    
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).with_for_update().first()
    
    if not inventory:
        raise ValueError("Product not found in inventory")
    
    if inventory.available_quantity < quantity:
        raise ValueError(f"Insufficient stock. Available: {inventory.available_quantity}")
    
    # Reserve stock
    inventory.reserved_quantity += quantity
    inventory.available_quantity = inventory.quantity - inventory.reserved_quantity
    
    # Record movement
    movement = StockMovement(
        product_id=product_id,
        movement_type="reservation",
        quantity=quantity,
        reference_type="order",
        reference_id=reference_id
    )
    db.add(movement)
    
    db.commit()
    return True
```

### 3. Deduct Stock (Sale Confirmed)

```python
def deduct_stock(
    db: Session,
    product_id: str,
    quantity: int,
    sale_id: str = None,
    user_id: str = None
) -> Inventory:
    """Deduct stock after confirmed sale."""
    
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).with_for_update().first()
    
    if not inventory:
        raise ValueError("Product not found in inventory")
    
    if inventory.quantity < quantity:
        raise ValueError(f"Insufficient stock. Current: {inventory.quantity}")
    
    # Deduct from both total and reserved
    inventory.quantity -= quantity
    if inventory.reserved_quantity >= quantity:
        inventory.reserved_quantity -= quantity
    else:
        inventory.reserved_quantity = 0
    
    inventory.available_quantity = inventory.quantity - inventory.reserved_quantity
    
    # Record movement
    movement = StockMovement(
        product_id=product_id,
        movement_type="sale",
        quantity=-quantity,  # Negative for deduction
        reference_type="sale",
        reference_id=sale_id,
        created_by=user_id
    )
    db.add(movement)
    
    db.commit()
    db.refresh(inventory)
    
    return inventory
```

### 4. Stock Adjustment

```python
def adjust_stock(
    db: Session,
    product_id: str,
    new_quantity: int,
    reason: str,
    user_id: str = None
) -> Inventory:
    """Manually adjust stock (for corrections, damage, etc.)."""
    
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).with_for_update().first()
    
    if not inventory:
        raise ValueError("Product not found in inventory")
    
    old_quantity = inventory.quantity
    difference = new_quantity - old_quantity
    
    # Update quantity
    inventory.quantity = new_quantity
    inventory.available_quantity = inventory.quantity - inventory.reserved_quantity
    
    # Record movement
    movement = StockMovement(
        product_id=product_id,
        movement_type="adjustment",
        quantity=difference,
        notes=f"Adjustment: {reason}",
        created_by=user_id
    )
    db.add(movement)
    
    db.commit()
    db.refresh(inventory)
    
    return inventory
```

---

## Low Stock Alerts

### Check Low Stock

```python
def get_low_stock_products(db: Session) -> list[dict]:
    """Get products with stock below threshold."""
    
    low_stock = db.query(Product, Inventory).join(
        Inventory, Product.id == Inventory.product_id
    ).filter(
        Inventory.quantity <= Inventory.low_stock_threshold
    ).all()
    
    return [
        {
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "current_stock": inventory.quantity,
            "threshold": inventory.low_stock_threshold,
            "status": "critical" if inventory.quantity == 0 else "low"
        }
        for product, inventory in low_stock
    ]
```

### Alert Notification

```python
async def send_low_stock_alert(
    workspace_id: str,
    products: list[dict]
):
    """Send low stock alert to workspace admins."""
    
    # Get workspace admins
    admins = db.query(User).join(WorkspaceUser).filter(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.role == "admin"
    ).all()
    
    # Send email/notification
    for admin in admins:
        await send_email(
            to=admin.email,
            subject="Low Stock Alert",
            body=render_template("low_stock_alert.html", products=products)
        )
```

---

## Multi-Channel Synchronization

### Sync Strategy

When a sale occurs on any marketplace:
1. Deduct from unified inventory
2. Update listings on ALL marketplaces
3. Prevent overselling

```python
async def sync_inventory_across_marketplaces(
    db: Session,
    product_id: str
):
    """Sync inventory to all marketplace listings."""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    
    available_qty = inventory.available_quantity
    
    # Update Mercado Livre
    if product.mercadolivre_id:
        await update_mercadolivre_stock(product.mercadolivre_id, available_qty)
    
    # Update Shopee
    if product.shopee_id:
        await update_shopee_stock(product.shopee_id, available_qty)
```

---

## Inventory Valuation

### FIFO (First In, First Out)

```python
def calculate_inventory_value_fifo(db: Session) -> Decimal:
    """Calculate total inventory value using FIFO method."""
    
    # Get all stock movements ordered by date
    movements = db.query(StockMovement).filter(
        StockMovement.movement_type.in_(["purchase", "sale"])
    ).order_by(StockMovement.created_at).all()
    
    # Calculate FIFO value
    # Implementation depends on detailed cost tracking
    pass
```

---

## API Endpoints

### Get Inventory Status

```python
@router.get("/inventory/{product_id}")
async def get_inventory_status(
    product_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Get current inventory status for a product."""
    
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    return {
        "product_id": product_id,
        "quantity": inventory.quantity,
        "reserved": inventory.reserved_quantity,
        "available": inventory.available_quantity,
        "location": inventory.location,
        "low_stock_threshold": inventory.low_stock_threshold,
        "is_low_stock": inventory.quantity <= inventory.low_stock_threshold,
        "last_updated": inventory.last_updated
    }
```

---

## Best Practices

1. **Always use transactions** for inventory operations
2. **Lock rows** when updating stock (with_for_update)
3. **Validate quantities** before operations
4. **Record all movements** for audit trail
5. **Sync immediately** after stock changes
6. **Monitor low stock** with scheduled jobs
7. **Use decimal** for costs, not float

---

## Related Agents

- **Pricing Agent**: Uses acquisition cost for price calculation
- **Marketplace Sync Agent**: Handles multi-channel updates
- **Database Agent**: Transaction patterns and locking

---

**Last Updated**: 2026-05-19  
**Version**: 1.0.0
