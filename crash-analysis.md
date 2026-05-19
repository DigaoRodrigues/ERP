# Application Crash Analysis

## Summary
The application is crashing during startup due to a configuration error when parsing the `ALLOWED_ORIGINS` environment variable.

## Root Cause
**Error Type**: `pydantic_settings.sources.SettingsError`  
**Location**: `app/core/config.py`, line 47  
**Specific Issue**: `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`

### Detailed Analysis

The crash occurs when Pydantic Settings attempts to initialize the `Settings()` class. The error trace shows:

```
File "/app/app/core/config.py", line 47, in <module>
  settings = Settings()
             ^^^^^^^^^^
```

The JSON decoder fails when trying to parse the `ALLOWED_ORIGINS` field, which suggests:

1. **The field is defined as a complex type** (likely `list[str]` or similar) in the Settings class
2. **The environment variable value is invalid** - either:
   - Empty or not set
   - Plain string format (e.g., `http://localhost:3000`) instead of JSON array format
   - Malformed JSON

### Expected vs Actual Format

**Expected format** (JSON array):
```bash
ALLOWED_ORIGINS='["http://localhost:3000","https://example.com"]'
```

**Problematic formats** that would cause this error:
```bash
ALLOWED_ORIGINS=                                    # Empty
ALLOWED_ORIGINS=http://localhost:3000               # Plain string
ALLOWED_ORIGINS=http://localhost:3000,https://...   # Comma-separated
```

## Solution

### Option 1: Fix Environment Variable (Recommended)
Set the `ALLOWED_ORIGINS` environment variable in Railway with proper JSON format:

```bash
ALLOWED_ORIGINS=["http://localhost:3000","https://your-domain.com"]
```

### Option 2: Update Code to Handle Plain Strings
Modify `backend/app/core/config.py` to accept both JSON arrays and comma-separated strings:

```python
from pydantic import field_validator

class Settings(BaseSettings):
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated string
            if ',' in v:
                return [origin.strip() for origin in v.split(',')]
            # Handle single string
            return [v]
        return v
```

### Option 3: Provide Default Value
Ensure the Settings class has a sensible default:

```python
ALLOWED_ORIGINS: list[str] = Field(
    default=["http://localhost:3000"],
    description="Allowed CORS origins"
)
```

## Immediate Action Required

1. **Check Railway environment variables** for the `ALLOWED_ORIGINS` setting
2. **Verify the format** matches JSON array syntax
3. **Redeploy** after fixing the environment variable

## Prevention

- Add validation in the Settings class to provide clearer error messages
- Document required environment variable formats in `.env.example`
- Add startup checks that fail gracefully with helpful error messages
- Consider using Railway's environment variable templates

## Related Files to Review

- `backend/app/core/config.py` - Settings configuration
- `backend/.env.example` - Environment variable documentation
- Railway dashboard - Environment variables configuration
