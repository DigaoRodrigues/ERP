# Contributing Guidelines

## Development Rules and Standards

This document outlines the development rules, standards, and best practices for the ERP Multi-Tenant System project.

## Table of Contents

1. [Code Standards](#code-standards)
2. [Git Workflow](#git-workflow)
3. [Testing Requirements](#testing-requirements)
4. [Documentation](#documentation)
5. [Security Guidelines](#security-guidelines)
6. [Performance Standards](#performance-standards)
7. [Code Review Process](#code-review-process)

---

## Code Standards

### Python (Backend)

#### Style Guide
- Follow **PEP 8** style guide strictly
- Use **type hints** for all function parameters and return values
- Maximum line length: **88 characters** (Black formatter standard)
- Use **docstrings** for all classes and functions (Google style)

#### Naming Conventions
```python
# Classes: PascalCase
class UserService:
    pass

# Functions/Methods: snake_case
def get_user_by_id(user_id: int) -> User:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3

# Private methods: _leading_underscore
def _internal_helper(self) -> None:
    pass
```

#### Code Organization
```python
# Import order (enforced by isort):
# 1. Standard library
import os
from typing import List, Optional

# 2. Third-party packages
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. Local application imports
from app.core.config import settings
from app.models.user import User
```

#### Required Tools
- **Black**: Code formatter
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pylint**: Additional linting

### TypeScript/React (Frontend)

#### Style Guide
- Follow **Airbnb TypeScript Style Guide**
- Use **functional components** with hooks (no class components)
- Use **TypeScript strict mode**
- Maximum line length: **100 characters**

#### Naming Conventions
```typescript
// Components: PascalCase
const UserProfile: React.FC<UserProfileProps> = () => {};

// Functions: camelCase
const fetchUserData = async (userId: string) => {};

// Constants: UPPER_SNAKE_CASE
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// Interfaces/Types: PascalCase with 'I' prefix for interfaces
interface IUserData {
  id: string;
  name: string;
}

type UserRole = 'admin' | 'operator' | 'viewer';
```

#### Component Structure
```typescript
// 1. Imports
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// 2. Types/Interfaces
interface ComponentProps {
  userId: string;
}

// 3. Component
export const Component: React.FC<ComponentProps> = ({ userId }) => {
  // 4. Hooks
  const router = useRouter();
  const [data, setData] = useState<Data | null>(null);

  // 5. Effects
  useEffect(() => {
    // ...
  }, [userId]);

  // 6. Handlers
  const handleClick = () => {
    // ...
  };

  // 7. Render
  return <div>{/* ... */}</div>;
};
```

#### Required Tools
- **ESLint**: Linting
- **Prettier**: Code formatting
- **TypeScript**: Type checking

---

## Git Workflow

### Branch Strategy

```
main (production)
  ├── staging (pre-production)
  │   ├── development (integration)
  │   │   ├── feature/feature-name
  │   │   ├── fix/bug-description
  │   │   └── refactor/refactor-description
```

### Branch Naming Convention

- **Feature branches**: `feature/short-description`
  - Example: `feature/user-authentication`
- **Bug fixes**: `fix/bug-description`
  - Example: `fix/cors-configuration-error`
- **Refactoring**: `refactor/what-is-refactored`
  - Example: `refactor/database-connection-pool`
- **Documentation**: `docs/what-is-documented`
  - Example: `docs/api-endpoints`

### Commit Message Format

Follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: CI/CD changes

#### Examples
```bash
# Good commits
feat(auth): add JWT refresh token rotation
fix(inventory): prevent negative stock values
docs(api): update authentication endpoints documentation
refactor(database): optimize query performance for product listing

# Bad commits (avoid these)
fix: fixed bug
update code
changes
WIP
```

### Pull Request Process

1. **Create feature branch** from `development`
2. **Make changes** following code standards
3. **Write tests** for new functionality
4. **Update documentation** if needed
5. **Run all checks locally**:
   ```bash
   # Backend
   cd backend
   black .
   isort .
   flake8 .
   mypy .
   pytest

   # Frontend
   cd frontend
   npm run lint
   npm run type-check
   npm run test
   ```
6. **Create Pull Request** to `development`
7. **Fill PR template** completely
8. **Request review** from at least one team member
9. **Address review comments**
10. **Merge** after approval

### PR Title Format
```
[TYPE] Brief description of changes

Examples:
[FEAT] Add user role-based access control
[FIX] Resolve CORS configuration error
[DOCS] Update deployment guide
```

---

## Testing Requirements

### Backend Testing

#### Minimum Coverage
- **Unit tests**: 80% coverage minimum
- **Integration tests**: Critical paths must be covered
- **E2E tests**: Main user flows

#### Test Structure
```python
# tests/test_user_service.py
import pytest
from app.services.user_service import UserService

class TestUserService:
    """Test suite for UserService."""

    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        # Arrange
        user_data = {"email": "test@example.com", "name": "Test User"}
        
        # Act
        user = UserService.create_user(db_session, user_data)
        
        # Assert
        assert user.email == "test@example.com"
        assert user.name == "Test User"

    def test_create_user_duplicate_email(self, db_session):
        """Test user creation with duplicate email fails."""
        # Arrange
        user_data = {"email": "test@example.com", "name": "Test User"}
        UserService.create_user(db_session, user_data)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            UserService.create_user(db_session, user_data)
```

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_user_service.py

# Run specific test
pytest tests/test_user_service.py::TestUserService::test_create_user_success
```

### Frontend Testing

#### Test Types
- **Unit tests**: Components, hooks, utilities
- **Integration tests**: Component interactions
- **E2E tests**: User flows (Playwright/Cypress)

#### Test Structure
```typescript
// __tests__/UserProfile.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserProfile } from '@/components/UserProfile';

describe('UserProfile', () => {
  it('renders user information correctly', () => {
    // Arrange
    const user = { id: '1', name: 'John Doe', email: 'john@example.com' };
    
    // Act
    render(<UserProfile user={user} />);
    
    // Assert
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('handles edit button click', async () => {
    // Arrange
    const onEdit = jest.fn();
    render(<UserProfile user={user} onEdit={onEdit} />);
    
    // Act
    await userEvent.click(screen.getByRole('button', { name: /edit/i }));
    
    // Assert
    await waitFor(() => {
      expect(onEdit).toHaveBeenCalledWith(user.id);
    });
  });
});
```

---

## Documentation

### Code Documentation

#### Python Docstrings (Google Style)
```python
def calculate_minimum_price(
    acquisition_cost: float,
    commission_rate: float,
    shipping_cost: float,
    profit_margin: float
) -> float:
    """Calculate the minimum viable selling price.

    Args:
        acquisition_cost: The cost to acquire the product.
        commission_rate: Marketplace commission rate (0.0 to 1.0).
        shipping_cost: Cost of shipping (if absorbed by seller).
        profit_margin: Desired profit margin (0.0 to 1.0).

    Returns:
        The minimum price to avoid selling at a loss.

    Raises:
        ValueError: If any rate is negative or greater than 1.

    Example:
        >>> calculate_minimum_price(100.0, 0.15, 10.0, 0.20)
        153.85
    """
    if commission_rate < 0 or commission_rate > 1:
        raise ValueError("Commission rate must be between 0 and 1")
    
    # Implementation...
```

#### TypeScript JSDoc
```typescript
/**
 * Fetches user data from the API.
 *
 * @param userId - The unique identifier of the user
 * @param options - Optional fetch configuration
 * @returns Promise resolving to user data
 * @throws {ApiError} When the API request fails
 *
 * @example
 * ```typescript
 * const user = await fetchUser('123');
 * console.log(user.name);
 * ```
 */
async function fetchUser(
  userId: string,
  options?: FetchOptions
): Promise<User> {
  // Implementation...
}
```

### API Documentation

- Use **FastAPI automatic documentation** (Swagger/OpenAPI)
- Add detailed descriptions to all endpoints
- Include request/response examples
- Document error responses

```python
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user account with the provided information.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "User with this email already exists"},
    },
)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Create a new user account.
    
    - **email**: Valid email address (required)
    - **name**: User's full name (required)
    - **role**: User role (admin, operator, viewer)
    """
    # Implementation...
```

### README Updates

Update README.md when:
- Adding new features
- Changing setup process
- Modifying environment variables
- Updating dependencies

---

## Security Guidelines

### Authentication & Authorization

1. **Never commit secrets** to version control
2. Use **environment variables** for sensitive data
3. Implement **JWT token rotation**
4. Enforce **strong password policies**
5. Use **HTTPS only** in production
6. Implement **rate limiting** on all endpoints

### Input Validation

```python
# Always validate and sanitize user input
from pydantic import BaseModel, EmailStr, constr, validator

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    name: constr(min_length=2, max_length=100)  # Length constraints
    password: constr(min_length=8)  # Minimum password length
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Ensure password meets security requirements."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
```

### SQL Injection Prevention

```python
# ✅ GOOD: Use ORM or parameterized queries
user = db.query(User).filter(User.email == email).first()

# ❌ BAD: Never use string concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"  # VULNERABLE!
```

### XSS Prevention

```typescript
// ✅ GOOD: React automatically escapes content
<div>{userInput}</div>

// ❌ BAD: Avoid dangerouslySetInnerHTML unless absolutely necessary
<div dangerouslySetInnerHTML={{ __html: userInput }} />  // VULNERABLE!
```

---

## Performance Standards

### Backend Performance

1. **Database queries**:
   - Use indexes on frequently queried columns
   - Implement pagination for large datasets
   - Use `select_related()` and `prefetch_related()` to avoid N+1 queries

2. **API response times**:
   - Simple queries: < 100ms
   - Complex queries: < 500ms
   - Implement caching for frequently accessed data

3. **Resource limits**:
   - Maximum request size: 10MB
   - Request timeout: 30 seconds
   - Rate limit: 60 requests/minute per workspace

### Frontend Performance

1. **Bundle size**:
   - Initial load: < 200KB (gzipped)
   - Use code splitting for routes
   - Lazy load components when appropriate

2. **Rendering**:
   - First Contentful Paint (FCP): < 1.5s
   - Time to Interactive (TTI): < 3.5s
   - Use React.memo() for expensive components

3. **Images**:
   - Use Next.js Image component
   - Implement lazy loading
   - Optimize image sizes

---

## Code Review Process

### Reviewer Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Performance impact is acceptable
- [ ] Error handling is appropriate
- [ ] Logging is adequate
- [ ] No commented-out code
- [ ] No console.log() statements in production code
- [ ] Environment variables are documented

### Review Comments

Use constructive language:

```
✅ GOOD:
"Consider using a Set here for O(1) lookup instead of Array.includes() 
which is O(n). This will improve performance for large datasets."

❌ BAD:
"This is slow. Fix it."
```

### Approval Criteria

- At least **one approval** required
- All **CI checks passing**
- No **unresolved comments**
- **Conflicts resolved**

---

## Development Environment Setup

### Required Tools

#### Backend
```bash
# Python 3.11+
python --version

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install
```

#### Frontend
```bash
# Node.js 18+
node --version

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88', '--extend-ignore=E203']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## Continuous Integration

### GitHub Actions Workflow

All PRs must pass:
1. **Linting** (Black, isort, flake8, ESLint)
2. **Type checking** (mypy, TypeScript)
3. **Tests** (pytest, Jest)
4. **Security scan** (Bandit, npm audit)
5. **Build** (Docker images)

### Deployment Pipeline

```
PR → development → staging → production
     ↓              ↓          ↓
   Auto-deploy  Manual review  Manual approval
```

---

## Questions or Suggestions?

If you have questions about these guidelines or suggestions for improvements:
1. Open an issue with the `question` or `enhancement` label
2. Discuss in team meetings
3. Submit a PR to update this document

---

**Last Updated**: 2026-05-19
**Version**: 1.0.0
