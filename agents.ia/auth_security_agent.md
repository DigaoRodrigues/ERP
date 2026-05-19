# Authentication & Security Agent

## Domain Overview

Expert in JWT authentication, role-based access control (RBAC), security best practices, and threat prevention for the ERP Multi-Tenant System.

## Core Responsibilities

- JWT token management and refresh token rotation
- Role-based access control (RBAC)
- Password hashing and validation
- Security vulnerability prevention
- API endpoint protection

---

## Authentication Architecture

### JWT Token Strategy

**Access Token**: Short-lived (30 minutes), used for API requests
**Refresh Token**: Long-lived (7 days), used to obtain new access tokens

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        return None
```

### Password Security

```python
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    return True, "Password is strong"
```

---

## Role-Based Access Control (RBAC)

### Role Definitions

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"        # Full access to workspace
    OPERATOR = "operator"  # Can create/edit data
    VIEWER = "viewer"      # Read-only access

# Permission matrix
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["read", "write", "delete", "manage_users"],
    UserRole.OPERATOR: ["read", "write"],
    UserRole.VIEWER: ["read"]
}
```

### Permission Checking

```python
from fastapi import Depends, HTTPException, status
from app.models.user import User

def require_permission(required_permission: str):
    """Decorator to check user permissions."""
    def permission_checker(
        current_user: User = Depends(get_current_user),
        workspace_id: str = Depends(get_current_workspace)
    ):
        # Get user role in workspace
        workspace_user = db.query(WorkspaceUser).filter(
            WorkspaceUser.workspace_id == workspace_id,
            WorkspaceUser.user_id == current_user.id
        ).first()
        
        if not workspace_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not in workspace"
            )
        
        user_permissions = ROLE_PERMISSIONS.get(workspace_user.role, [])
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        
        return current_user
    
    return permission_checker

# Usage in endpoint
@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    current_user: User = Depends(require_permission("delete"))
):
    # Delete product logic
    pass
```

---

## Authentication Endpoints

### Login

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens."""
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

### Token Refresh

```python
@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Get new access token using refresh token."""
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    new_access_token = create_access_token({"sub": str(user.id)})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
```

---

## Security Best Practices

### 1. Input Validation

```python
from pydantic import BaseModel, EmailStr, constr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=100)
    full_name: constr(min_length=2, max_length=255)
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v
    
    @validator('full_name')
    def validate_name(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError("Name cannot contain numbers")
        return v.strip()
```

### 2. SQL Injection Prevention

```python
# ✅ GOOD: Use ORM
user = db.query(User).filter(User.email == email).first()

# ✅ GOOD: Use parameterized queries
result = db.execute(
    "SELECT * FROM users WHERE email = :email",
    {"email": email}
)

# ❌ BAD: String concatenation (NEVER DO THIS)
query = f"SELECT * FROM users WHERE email = '{email}'"  # VULNERABLE!
```

### 3. XSS Prevention

```python
from html import escape

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    return escape(text)

# Use in Pydantic validators
@validator('description')
def sanitize_description(cls, v):
    return sanitize_input(v) if v else v
```

### 4. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Never use ["*"] in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests
)
```

### 5. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, ...):
    pass
```

---

## Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS redirect in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## Secrets Management

### Environment Variables

```python
# ✅ GOOD: Use environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# ❌ BAD: Hardcoded secrets
JWT_SECRET_KEY = "my-secret-key-123"  # NEVER DO THIS
```

### Secret Rotation

```bash
# Generate strong secret
openssl rand -hex 32

# Rotate JWT secret
# 1. Generate new secret
# 2. Update environment variable
# 3. Invalidate all existing tokens (optional)
# 4. Users re-authenticate
```

---

## Audit Logging

```python
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {'schema': 'public'}
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("public.users.id"))
    workspace_id = Column(UUID, ForeignKey("public.workspaces.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

def log_action(
    db: Session,
    user_id: str,
    workspace_id: str,
    action: str,
    resource_type: str = None,
    resource_id: str = None,
    request: Request = None
):
    """Log user action for audit trail."""
    audit_log = AuditLog(
        user_id=user_id,
        workspace_id=workspace_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(audit_log)
    db.commit()
```

---

## Common Vulnerabilities

### 1. Broken Authentication

```python
# ❌ BAD: No token expiration
token = jwt.encode({"sub": user_id}, SECRET_KEY)

# ✅ GOOD: Token with expiration
token = jwt.encode(
    {"sub": user_id, "exp": datetime.utcnow() + timedelta(minutes=30)},
    SECRET_KEY
)
```

### 2. Insecure Direct Object References

```python
# ❌ BAD: No authorization check
@router.get("/products/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.id == product_id).first()

# ✅ GOOD: Verify workspace access
@router.get("/products/{product_id}")
async def get_product(
    product_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    # Workspace schema is already set by get_current_workspace
    return db.query(Product).filter(Product.id == product_id).first()
```

### 3. Mass Assignment

```python
# ❌ BAD: Accept all fields from request
@router.put("/users/{user_id}")
async def update_user(user_id: str, user_data: dict):
    user.update(**user_data)  # Could update is_admin, etc.

# ✅ GOOD: Use Pydantic model with specific fields
class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    # is_admin is NOT included

@router.put("/users/{user_id}")
async def update_user(user_id: str, user_data: UserUpdate):
    user.update(**user_data.dict(exclude_unset=True))
```

---

## Security Checklist

- [ ] JWT tokens have expiration
- [ ] Refresh token rotation implemented
- [ ] Passwords hashed with bcrypt
- [ ] Password strength validation
- [ ] RBAC enforced on all endpoints
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (ORM/parameterized queries)
- [ ] XSS prevention (input sanitization)
- [ ] CORS properly configured
- [ ] Rate limiting on authentication endpoints
- [ ] Security headers set
- [ ] HTTPS enforced in production
- [ ] Secrets in environment variables
- [ ] Audit logging implemented
- [ ] No sensitive data in logs
- [ ] Regular security audits

---

## Related Agents

- **API Design Agent**: Endpoint protection patterns
- **Multi-Tenancy Agent**: Workspace-level authorization
- **Database Agent**: Secure query patterns

---

**Last Updated**: 2026-05-19  
**Version**: 1.0.0
