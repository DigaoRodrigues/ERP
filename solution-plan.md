# Solution Plan: Fix ALLOWED_ORIGINS Configuration Error

## Problem Statement
The application crashes because Railway's `ALLOWED_ORIGINS` environment variable is set as a plain string (`http://localhost:3000`), but the code expects a JSON array format.

## Current Configuration
**File**: `backend/app/core/config.py`
```python
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

**Railway Environment Variable**:
```
ALLOWED_ORIGINS=http://localhost:3000
```

## Root Cause
Pydantic Settings automatically tries to parse complex types (like `List[str]`) as JSON. When it receives a plain string instead of a JSON array, it fails with `JSONDecodeError`.

## Recommended Solution: Add Field Validator

Modify `backend/app/core/config.py` to accept multiple input formats:

```python
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ... other fields ...
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """
        Parse ALLOWED_ORIGINS from various formats:
        - JSON array: ["http://localhost:3000","https://example.com"]
        - Comma-separated: http://localhost:3000,https://example.com
        - Single string: http://localhost:3000
        - List (already parsed): ["http://localhost:3000"]
        """
        if isinstance(v, str):
            # Try to parse as JSON first
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # Handle comma-separated string
            if ',' in v:
                return [origin.strip() for origin in v.split(',') if origin.strip()]
            
            # Handle single string
            if v.strip():
                return [v.strip()]
            
            # Empty string - return default
            return ["http://localhost:3000", "http://localhost:8000"]
        
        # Already a list
        if isinstance(v, list):
            return v
        
        # Fallback to default
        return ["http://localhost:3000", "http://localhost:8000"]
    
    # ... rest of config ...
```

## Implementation Steps

### Step 1: Update config.py
Add the `field_validator` to handle multiple input formats for `ALLOWED_ORIGINS`.

### Step 2: Update .env.example
Document the supported formats:

```bash
# CORS Configuration - Allowed Origins
# Supports multiple formats:
# - JSON array: ALLOWED_ORIGINS=["http://localhost:3000","https://example.com"]
# - Comma-separated: ALLOWED_ORIGINS=http://localhost:3000,https://example.com
# - Single value: ALLOWED_ORIGINS=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000
```

### Step 3: Test Locally
```bash
# Test with plain string
export ALLOWED_ORIGINS=http://localhost:3000
python -m uvicorn app.main:app --reload

# Test with comma-separated
export ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Test with JSON array
export ALLOWED_ORIGINS='["http://localhost:3000","http://localhost:8000"]'
```

### Step 4: Deploy to Railway
The existing environment variable (`ALLOWED_ORIGINS=http://localhost:3000`) will now work without changes.

### Step 5: Add Production Origins
Update Railway environment variable to include production domain:
```
ALLOWED_ORIGINS=http://localhost:3000,https://your-production-domain.railway.app
```

## Benefits of This Approach

1. **Backward Compatible**: Existing JSON array format still works
2. **User Friendly**: Plain strings and comma-separated values work
3. **Flexible**: Supports multiple deployment scenarios
4. **No Railway Changes Needed**: Current environment variable works as-is
5. **Robust**: Handles edge cases (empty strings, whitespace, etc.)

## Alternative Solutions (Not Recommended)

### Alternative 1: Change Railway Variable to JSON
**Pros**: No code changes needed  
**Cons**: Less user-friendly, easy to make syntax errors

### Alternative 2: Use String Type with Manual Parsing
**Pros**: Simpler type definition  
**Cons**: Loses type safety, more manual parsing logic

## Testing Checklist

- [ ] Test with plain string: `http://localhost:3000`
- [ ] Test with comma-separated: `http://localhost:3000,http://localhost:8000`
- [ ] Test with JSON array: `["http://localhost:3000"]`
- [ ] Test with empty string (should use defaults)
- [ ] Test with whitespace handling
- [ ] Verify CORS works in browser
- [ ] Check Railway deployment logs

## Next Steps

1. Switch to `code` mode to implement the solution
2. Update `backend/app/core/config.py` with the field validator
3. Update `backend/.env.example` with documentation
4. Test locally with different formats
5. Commit and push changes
6. Deploy to Railway
7. Verify application starts successfully
