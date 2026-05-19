# Pricing Engine Agent

## Domain Overview

Expert in pricing calculations, commission handling, profit margin analysis, and minimum viable price determination for marketplace products.

## Core Responsibilities

- Calculate minimum viable selling price
- Handle marketplace-specific commission rates
- Factor in shipping costs
- Ensure profit margins
- Prevent selling at a loss

---

## Business Context

### Problem Statement

Marketplace sellers need to:
- Calculate prices that cover all costs
- Account for different commission rates per marketplace and category
- Include shipping costs when absorbed by seller
- Maintain desired profit margins
- Avoid selling at a loss

### Key Challenges

1. **Variable Commission Rates**: Different rates for ML and Shopee by category
2. **Shipping Costs**: Sometimes absorbed by seller, sometimes by buyer
3. **Dynamic Pricing**: Adjust prices based on competition
4. **Multi-Currency**: Handle different currencies (BRL primarily)

---

## Pricing Formula

### Base Formula

```
Minimum Price = (Acquisition Cost + Shipping Cost) / (1 - Commission Rate - Profit Margin)
```

### Example Calculation

```python
Acquisition Cost: R$ 100.00
Shipping Cost: R$ 15.00 (absorbed by seller)
Commission Rate: 15% (0.15)
Desired Profit Margin: 20% (0.20)

Minimum Price = (100 + 15) / (1 - 0.15 - 0.20)
              = 115 / 0.65
              = R$ 176.92
```

---

## Data Model

### Marketplace Commission Rates

```python
from sqlalchemy import Column, String, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID

class MarketplaceCommission(Base):
    """Commission rates by marketplace and category."""
    __tablename__ = "marketplace_commissions"
    __table_args__ = {'schema': 'public'}  # Shared across workspaces
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    marketplace = Column(String(50), nullable=False)  # mercadolivre, shopee
    category = Column(String(100), nullable=False)
    commission_rate = Column(Numeric(5, 4), nullable=False)  # 0.1500 = 15%
    is_active = Column(Boolean, default=True)
    effective_date = Column(Date, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('marketplace', 'category', 'effective_date'),
    )
```

### Product Pricing

```python
class ProductPricing(Base):
    """Pricing information for products."""
    __tablename__ = "product_pricing"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID, ForeignKey("products.id"), nullable=False)
    
    # Costs
    acquisition_cost = Column(Numeric(10, 2), nullable=False)
    shipping_cost = Column(Numeric(10, 2), default=0)
    other_costs = Column(Numeric(10, 2), default=0)  # packaging, handling, etc.
    
    # Pricing strategy
    desired_profit_margin = Column(Numeric(5, 4), default=0.20)  # 20%
    
    # Calculated prices per marketplace
    mercadolivre_price = Column(Numeric(10, 2))
    shopee_price = Column(Numeric(10, 2))
    
    # Metadata
    last_calculated = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="pricing")
```

---

## Core Pricing Functions

### 1. Calculate Minimum Price

```python
from decimal import Decimal, ROUND_UP

def calculate_minimum_price(
    acquisition_cost: Decimal,
    commission_rate: Decimal,
    shipping_cost: Decimal = Decimal("0"),
    other_costs: Decimal = Decimal("0"),
    profit_margin: Decimal = Decimal("0.20")
) -> Decimal:
    """
    Calculate minimum viable selling price.
    
    Args:
        acquisition_cost: Cost to acquire the product
        commission_rate: Marketplace commission (0.0 to 1.0)
        shipping_cost: Shipping cost if absorbed by seller
        other_costs: Additional costs (packaging, handling)
        profit_margin: Desired profit margin (0.0 to 1.0)
    
    Returns:
        Minimum selling price to avoid loss
    
    Raises:
        ValueError: If rates are invalid or calculation impossible
    """
    # Validate inputs
    if commission_rate < 0 or commission_rate >= 1:
        raise ValueError("Commission rate must be between 0 and 1")
    
    if profit_margin < 0 or profit_margin >= 1:
        raise ValueError("Profit margin must be between 0 and 1")
    
    if commission_rate + profit_margin >= 1:
        raise ValueError("Commission + profit margin must be less than 100%")
    
    # Calculate total costs
    total_costs = acquisition_cost + shipping_cost + other_costs
    
    # Calculate minimum price
    # Price = Costs / (1 - Commission - Margin)
    divisor = Decimal("1") - commission_rate - profit_margin
    
    if divisor <= 0:
        raise ValueError("Cannot calculate price: commission + margin >= 100%")
    
    minimum_price = total_costs / divisor
    
    # Round up to nearest cent
    return minimum_price.quantize(Decimal("0.01"), rounding=ROUND_UP)
```

### 2. Get Commission Rate

```python
def get_commission_rate(
    db: Session,
    marketplace: str,
    category: str,
    date: datetime = None
) -> Decimal:
    """Get current commission rate for marketplace and category."""
    
    if date is None:
        date = datetime.now().date()
    
    commission = db.query(MarketplaceCommission).filter(
        MarketplaceCommission.marketplace == marketplace,
        MarketplaceCommission.category == category,
        MarketplaceCommission.effective_date <= date,
        MarketplaceCommission.is_active == True
    ).order_by(
        MarketplaceCommission.effective_date.desc()
    ).first()
    
    if not commission:
        # Default rates if not found
        default_rates = {
            "mercadolivre": Decimal("0.15"),  # 15%
            "shopee": Decimal("0.12")          # 12%
        }
        return default_rates.get(marketplace, Decimal("0.15"))
    
    return commission.commission_rate
```

### 3. Calculate Price for All Marketplaces

```python
def calculate_marketplace_prices(
    db: Session,
    product_id: str,
    acquisition_cost: Decimal,
    shipping_cost: Decimal = Decimal("0"),
    profit_margin: Decimal = Decimal("0.20")
) -> dict:
    """Calculate optimal price for each marketplace."""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise ValueError("Product not found")
    
    prices = {}
    
    # Mercado Livre
    ml_commission = get_commission_rate(db, "mercadolivre", product.category)
    prices["mercadolivre"] = calculate_minimum_price(
        acquisition_cost=acquisition_cost,
        commission_rate=ml_commission,
        shipping_cost=shipping_cost,
        profit_margin=profit_margin
    )
    
    # Shopee
    shopee_commission = get_commission_rate(db, "shopee", product.category)
    prices["shopee"] = calculate_minimum_price(
        acquisition_cost=acquisition_cost,
        commission_rate=shopee_commission,
        shipping_cost=shipping_cost,
        profit_margin=profit_margin
    )
    
    return prices
```

---

## Profit Analysis

### Calculate Actual Profit

```python
def calculate_profit(
    sale_price: Decimal,
    acquisition_cost: Decimal,
    commission_rate: Decimal,
    shipping_cost: Decimal = Decimal("0"),
    other_costs: Decimal = Decimal("0")
) -> dict:
    """Calculate actual profit from a sale."""
    
    # Calculate commission
    commission_amount = sale_price * commission_rate
    
    # Calculate total costs
    total_costs = acquisition_cost + shipping_cost + other_costs + commission_amount
    
    # Calculate profit
    gross_profit = sale_price - acquisition_cost - shipping_cost - other_costs
    net_profit = sale_price - total_costs
    profit_margin = (net_profit / sale_price) if sale_price > 0 else Decimal("0")
    
    return {
        "sale_price": sale_price,
        "acquisition_cost": acquisition_cost,
        "shipping_cost": shipping_cost,
        "other_costs": other_costs,
        "commission_amount": commission_amount,
        "total_costs": total_costs,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "profit_margin": profit_margin,
        "profit_margin_percent": profit_margin * 100
    }
```

### Profit Margin Analysis

```python
def analyze_profit_margins(
    db: Session,
    start_date: date,
    end_date: date
) -> dict:
    """Analyze profit margins over a period."""
    
    sales = db.query(Sale).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).all()
    
    total_revenue = Decimal("0")
    total_profit = Decimal("0")
    
    for sale in sales:
        product = sale.product
        profit_data = calculate_profit(
            sale_price=sale.unit_price,
            acquisition_cost=product.acquisition_cost,
            commission_rate=sale.commission_rate,
            shipping_cost=sale.shipping_cost
        )
        
        total_revenue += sale.unit_price * sale.quantity
        total_profit += profit_data["net_profit"] * sale.quantity
    
    overall_margin = (total_profit / total_revenue) if total_revenue > 0 else Decimal("0")
    
    return {
        "period": {"start": start_date, "end": end_date},
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "profit_margin": overall_margin,
        "profit_margin_percent": overall_margin * 100
    }
```

---

## Dynamic Pricing Strategies

### Competitive Pricing

```python
def suggest_competitive_price(
    db: Session,
    product_id: str,
    marketplace: str,
    competitor_prices: list[Decimal]
) -> dict:
    """Suggest competitive price based on market analysis."""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    # Calculate minimum viable price
    commission_rate = get_commission_rate(db, marketplace, product.category)
    min_price = calculate_minimum_price(
        acquisition_cost=product.acquisition_cost,
        commission_rate=commission_rate,
        profit_margin=Decimal("0.10")  # Minimum 10% margin
    )
    
    # Analyze competitor prices
    if competitor_prices:
        avg_competitor_price = sum(competitor_prices) / len(competitor_prices)
        min_competitor_price = min(competitor_prices)
        max_competitor_price = max(competitor_prices)
    else:
        avg_competitor_price = min_price
        min_competitor_price = min_price
        max_competitor_price = min_price
    
    # Pricing strategy
    if min_price > max_competitor_price:
        # Can't compete profitably
        suggested_price = min_price
        strategy = "minimum_viable"
        warning = "Minimum price exceeds market maximum"
    elif min_price > avg_competitor_price:
        # Above average but below max
        suggested_price = min_price
        strategy = "premium"
        warning = "Price above market average"
    else:
        # Can compete - price slightly below average
        suggested_price = avg_competitor_price * Decimal("0.95")
        if suggested_price < min_price:
            suggested_price = min_price
        strategy = "competitive"
        warning = None
    
    return {
        "suggested_price": suggested_price,
        "minimum_price": min_price,
        "strategy": strategy,
        "market_analysis": {
            "average": avg_competitor_price,
            "minimum": min_competitor_price,
            "maximum": max_competitor_price
        },
        "warning": warning
    }
```

---

## API Endpoints

### Calculate Price

```python
@router.post("/pricing/calculate")
async def calculate_price(
    request: PriceCalculationRequest,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Calculate minimum viable price."""
    
    try:
        commission_rate = get_commission_rate(
            db,
            request.marketplace,
            request.category
        )
        
        price = calculate_minimum_price(
            acquisition_cost=request.acquisition_cost,
            commission_rate=commission_rate,
            shipping_cost=request.shipping_cost,
            other_costs=request.other_costs,
            profit_margin=request.profit_margin
        )
        
        return {
            "minimum_price": price,
            "commission_rate": commission_rate,
            "profit_margin": request.profit_margin,
            "breakdown": {
                "acquisition_cost": request.acquisition_cost,
                "shipping_cost": request.shipping_cost,
                "other_costs": request.other_costs,
                "commission_amount": price * commission_rate,
                "profit_amount": price * request.profit_margin
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Best Practices

1. **Always round up** prices to avoid losses
2. **Validate inputs** before calculations
3. **Use Decimal** for all monetary values
4. **Store commission rates** in database for flexibility
5. **Track historical rates** for accurate profit analysis
6. **Consider all costs** in calculations
7. **Provide warnings** when pricing is not competitive

---

## Related Agents

- **Inventory Agent**: Uses acquisition cost from inventory
- **Financial Agent**: Profit analysis feeds into financial reports
- **Marketplace Sync Agent**: Applies calculated prices to listings

---

**Last Updated**: 2026-05-19  
**Version**: 1.0.0
