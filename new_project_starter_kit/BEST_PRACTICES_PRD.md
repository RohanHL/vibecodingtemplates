# Code Architecture Best Practices PRD

## Purpose
This document serves as a checklist and reference guide for architecting production-ready applications. Use this PRD to review new features, refactorings, or new projects before deployment to prevent common pitfalls.

**Last Updated:** 2025-10-31
**Version:** 1.0

---

## 🎯 Review Checklist

Before deploying ANY new feature or application, review against these categories:

- [ ] **Data Sources & APIs** - All 7 checkpoints passed
- [ ] **Database Design** - All 9 checkpoints passed
- [ ] **Error Handling** - All 6 checkpoints passed
- [ ] **Testing & Diagnostics** - All 8 checkpoints passed
- [ ] **Environment & Deployment** - All 10 checkpoints passed
- [ ] **Code Organization** - All 7 checkpoints passed
- [ ] **Performance & Caching** - All 6 checkpoints passed

---

## 1. Data Sources & APIs

### 1.1 API Selection Priority

**Priority Order (Highest to Lowest):**

1. **Official Paid APIs** (Finnhub, Alpha Vantage Pro, etc.)
   - Most reliable
   - Rate limits are predictable
   - SLAs and support
   - **Use for:** Production-critical data

2. **Official Free APIs** (Free tiers of above)
   - Good reliability
   - Lower rate limits
   - No SLA but documented
   - **Use for:** MVP and moderate-scale production

3. **Unofficial but Stable Libraries** (yfinance, pandas_datareader)
   - Moderate reliability
   - Can break without notice
   - No support
   - **Use for:** Non-critical fallbacks only

4. **Web Scraping**
   - Least reliable
   - Breaks when HTML changes
   - Legal concerns
   - **Use for:** Last resort fallbacks only

### 1.2 API Integration Checklist

**For EVERY external API integration:**

- [ ] **Rate Limits**
  - Documented the API rate limit (e.g., "60 calls/minute")
  - Implemented rate limiting in code
  - Added retry logic with exponential backoff
  - Logged when approaching rate limits

- [ ] **Error Handling**
  - Handle network timeouts (set max timeout: 10-30s)
  - Handle HTTP errors (400s, 500s)
  - Handle empty responses (null checks)
  - Handle malformed JSON/data
  - Never silently swallow errors

- [ ] **Fallback Strategy**
  - Primary source defined
  - Secondary source defined (if needed)
  - Tertiary source defined (if needed)
  - Documented cascade order in code comments
  - Each fallback attempts to get COMPLETE data, not partial

- [ ] **Environment Variables**
  - API keys stored in `.env` file
  - Never hardcoded in source code
  - Documented in `.env.example`
  - Validated on startup (log if missing)

- [ ] **Monitoring**
  - Log every API call (at DEBUG level)
  - Log every API failure (at WARNING/ERROR level)
  - Track success rates in production
  - Set up alerts for sustained failures

- [ ] **Documentation**
  - API provider documented
  - Rate limits documented
  - Cost structure documented (free tier limits)
  - Example requests/responses in code comments

### 1.3 Never Do This ❌

```python
# ❌ WRONG - Hardcoded fallback values
if api_failed:
    return "N/A"  # NEVER hardcode when you can fetch from another source

# ❌ WRONG - Silent failures
try:
    data = api.fetch()
except:
    pass  # Silently fails, no logging

# ❌ WRONG - Web scraping without API fallback
if page_text.count('buy') > page_text.count('sell'):
    return "Buy"  # Naive keyword counting

# ❌ WRONG - No timeout
response = requests.get(url)  # Can hang forever
```

### 1.4 Do This Instead ✅

```python
# ✅ CORRECT - Proper fallback chain
def get_analyst_recommendation(self, symbol: str) -> str:
    """
    Get analyst recommendation using multi-source fallback.

    Priority order:
    1. Finnhub API (primary, 60 calls/min free tier)
    2. yfinance (fallback, unreliable in production)
    3. Return "N/A" if all sources fail
    """
    # Primary: Finnhub API
    try:
        logger.info(f"Fetching analyst rating for {symbol} (Finnhub primary)")
        response = requests.get(
            f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}",
            headers={'Authorization': f'Bearer {self.finnhub_key}'},
            timeout=10  # Always set timeout
        )

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # Process structured data
                latest = data[0]
                buy_votes = latest.get('strongBuy', 0) + latest.get('buy', 0)
                sell_votes = latest.get('sell', 0) + latest.get('strongSell', 0)
                hold_votes = latest.get('hold', 0)

                if buy_votes > sell_votes and buy_votes > hold_votes:
                    logger.info(f"✅ Finnhub success for {symbol}: Buy")
                    return "Buy"
                elif sell_votes > buy_votes and sell_votes > hold_votes:
                    return "Sell"
                else:
                    return "Hold"
        else:
            logger.warning(f"Finnhub returned {response.status_code} for {symbol}")

    except requests.Timeout:
        logger.warning(f"Finnhub timeout for {symbol}, trying fallback")
    except Exception as e:
        logger.warning(f"Finnhub failed for {symbol}: {str(e)}, trying fallback")

    # Fallback: yfinance
    try:
        logger.info(f"Fetching analyst rating for {symbol} (yfinance fallback)")
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if 'recommendationMean' in info:
            # Process yfinance data
            mean = info['recommendationMean']
            if mean <= 2.0:
                return "Buy"
            elif mean >= 4.0:
                return "Sell"
            else:
                return "Hold"

    except Exception as e:
        logger.warning(f"yfinance failed for {symbol}: {str(e)}")

    # All sources failed - return N/A (explicit, not guessing)
    logger.info(f"All sources failed for {symbol}, returning N/A")
    return "N/A"
```

---

## 2. Database Design

### 2.1 Database Selection

**When to use SQLite:**
- Local development only
- Prototyping
- Single-user applications
- Embedded applications

**When to use PostgreSQL:**
- Production deployments
- Multi-user applications
- Applications requiring:
  - Concurrent writes
  - ACID transactions
  - JSON columns with indexing
  - Full-text search
  - Row-level locking

**NEVER use SQLite in production for multi-user web applications.**

### 2.2 Schema Design Checklist

**For EVERY new table:**

- [ ] **Primary Key**
  - Use `id = Column(Integer, primary_key=True, autoincrement=True)`
  - For PostgreSQL: Explicitly use SERIAL or Sequence
  - Never use `sqlite_autoincrement=True` (SQLite-specific)

- [ ] **Timestamps**
  - `created_at = Column(DateTime, default=datetime.utcnow, nullable=False)`
  - `updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)`
  - Always use UTC (not local time)
  - Index timestamp columns used for filtering

- [ ] **Indexes**
  - Index foreign keys
  - Index columns used in WHERE clauses
  - Index columns used in ORDER BY
  - Composite indexes for common query patterns
  - Don't over-index (slows writes)

- [ ] **Constraints**
  - Add NOT NULL where appropriate
  - Add UNIQUE constraints where needed
  - Add CHECK constraints for data validation
  - Add foreign key constraints with proper CASCADE behavior

- [ ] **Status/State Fields**
  - Use enums or constrained strings
  - Document all possible values in comments
  - Index status fields if used for filtering
  - Example: `status = Column(String(20), default="active")  # active, inactive, deleted`

- [ ] **JSON Columns**
  - Use for flexible/nested data only
  - Document expected schema in docstring
  - Don't abuse JSON - use proper columns when possible
  - For PostgreSQL: Use JSONB, not JSON (faster)

### 2.3 Migration Strategy

**Required for ALL projects:**

- [ ] **Use Alembic (or equivalent migration tool)**
  - Install: `pip install alembic`
  - Initialize: `alembic init alembic`
  - Generate migrations: `alembic revision --autogenerate -m "description"`
  - Apply migrations: `alembic upgrade head`

- [ ] **Migration Best Practices**
  - One migration per logical change
  - Descriptive migration names
  - Test migrations on staging before production
  - Always write `downgrade()` functions
  - Never edit applied migrations (create new ones)

- [ ] **Schema Synchronization**
  - Keep local, staging, and production schemas in sync
  - Document migration process in README
  - Run migrations as part of deployment pipeline

### 2.4 PostgreSQL-Specific Considerations

**For Railway/Production PostgreSQL deployments:**

- [ ] **Sequences**
  - Check sequences after data imports/migrations
  - Reset sequences if they get out of sync:
    ```sql
    SELECT setval('table_name_id_seq', (SELECT MAX(id) FROM table_name) + 1);
    ```

- [ ] **Connection Pooling**
  - Configure SQLAlchemy pool size:
    ```python
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,          # Max connections in pool
        max_overflow=10,      # Additional connections if needed
        pool_pre_ping=True,   # Verify connections before use
        pool_recycle=3600     # Recycle connections every hour
    )
    ```

- [ ] **Environment Differences**
  - SQLite uses `?` for parameters, PostgreSQL uses `%s`
  - SQLite auto-converts types, PostgreSQL is strict
  - Test data type conversions (JSON, DateTime, etc.)
  - Use SQLAlchemy abstractions to avoid dialect-specific code

### 2.5 Never Do This ❌

```python
# ❌ WRONG - SQLite-specific autoincrement
class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True)
    __table_args__ = (
        {'sqlite_autoincrement': True},  # Ignored by PostgreSQL!
    )

# ❌ WRONG - Manual table creation
MyModel.__table__.create(engine)  # Ad-hoc, no migration history

# ❌ WRONG - No timestamps
class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True)
    data = Column(String(100))
    # No created_at, no updated_at

# ❌ WRONG - Using local time
created_at = Column(DateTime, default=datetime.now)  # Local time!
```

### 2.6 Do This Instead ✅

```python
# ✅ CORRECT - Cross-database compatible
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from datetime import datetime

class MyModel(Base):
    """
    My model description.

    Tracks [what this model represents].

    Indexes:
    - id: Primary key
    - created_at: For time-based queries
    - status: For filtering active records
    """
    __tablename__ = "my_models"

    # Primary key with autoincrement (works for SQLite and PostgreSQL)
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Data columns
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active", index=True)  # active, inactive, deleted

    # Metadata columns (always include)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Use Alembic for migrations
    # > alembic revision --autogenerate -m "Add MyModel table"
    # > alembic upgrade head
```

---

## 3. Error Handling

### 3.1 Error Handling Principles

**The Four Commandments:**

1. **Never Silently Fail** - Always log errors
2. **Fail Fast** - Don't hide errors under layers of try/except
3. **Provide Context** - Log what you were trying to do when it failed
4. **Graceful Degradation** - Return meaningful error messages to users

### 3.2 Logging Checklist

**For EVERY function that can fail:**

- [ ] **Log Levels**
  - `DEBUG`: Detailed diagnostic info (every API call, every query)
  - `INFO`: General informational messages (successful operations)
  - `WARNING`: Something unexpected but recoverable (API fallback used)
  - `ERROR`: Error occurred but application continues (caught exception)
  - `CRITICAL`: Application cannot continue (database down)

- [ ] **Log Content**
  - What operation was being attempted
  - Input parameters (sanitize sensitive data!)
  - Error message from exception
  - Stack trace for errors
  - Timestamp (automatic with logging)

- [ ] **Structured Logging**
  ```python
  logger.info(f"Fetching data for {symbol} from {source}")
  logger.warning(f"API {source} failed for {symbol}: {error}, trying fallback")
  logger.error(f"All sources failed for {symbol}: {error}", exc_info=True)
  ```

### 3.3 Exception Handling Patterns

**Pattern 1: Cascade Fallback**
```python
def get_data(symbol):
    """
    Try multiple sources with proper error handling.
    """
    # Primary source
    try:
        logger.info(f"Fetching {symbol} from primary source")
        return fetch_from_primary(symbol)
    except PrimaryAPIError as e:
        logger.warning(f"Primary source failed for {symbol}: {e}, trying fallback")

    # Fallback source
    try:
        logger.info(f"Fetching {symbol} from fallback source")
        return fetch_from_fallback(symbol)
    except FallbackAPIError as e:
        logger.error(f"Fallback source failed for {symbol}: {e}")

    # All sources failed
    logger.error(f"All sources failed for {symbol}")
    return None
```

**Pattern 2: Retry with Exponential Backoff**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_with_retry(url):
    """
    Retry failed requests with exponential backoff.

    Attempts: 3 times
    Wait: 2s, 4s, 8s
    """
    logger.debug(f"Attempting to fetch {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

**Pattern 3: Database Transaction Error Handling**
```python
def save_data(db: Session, data: dict):
    """
    Save data with proper transaction handling.
    """
    try:
        obj = MyModel(**data)
        db.add(obj)
        db.commit()
        logger.info(f"Successfully saved {obj.id}")
        return obj
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error saving data: {e}")
        raise HTTPException(status_code=400, detail="Duplicate entry")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error saving data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")
```

### 3.4 Never Do This ❌

```python
# ❌ WRONG - Silent failure
try:
    data = fetch_data()
except:
    pass  # User has no idea what failed

# ❌ WRONG - Bare except
try:
    data = fetch_data()
except:  # Catches KeyboardInterrupt, SystemExit, etc!
    return None

# ❌ WRONG - Swallowing errors in production
try:
    data = fetch_data()
except Exception as e:
    print(f"Error: {e}")  # Prints to stdout, not logged
    return "default_value"

# ❌ WRONG - No context in error messages
logger.error("Failed")  # What failed? What were you doing?
```

### 3.5 Do This Instead ✅

```python
# ✅ CORRECT - Proper error handling with context
def fetch_analyst_rating(symbol: str) -> str:
    """
    Fetch analyst rating with proper error handling.

    Args:
        symbol: Stock ticker symbol

    Returns:
        "Buy", "Sell", "Hold", or "N/A"
    """
    try:
        logger.info(f"Fetching analyst rating for {symbol}")

        # Primary API
        response = requests.get(
            f"https://api.example.com/rating/{symbol}",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        rating = data.get('rating')

        if not rating:
            logger.warning(f"No rating found for {symbol} in API response")
            return "N/A"

        logger.info(f"✅ Successfully fetched rating for {symbol}: {rating}")
        return rating

    except requests.Timeout:
        logger.error(f"Timeout fetching rating for {symbol} after 10s")
        return "N/A"

    except requests.HTTPError as e:
        logger.error(f"HTTP error fetching rating for {symbol}: {e.response.status_code}")
        return "N/A"

    except KeyError as e:
        logger.error(f"Unexpected API response format for {symbol}: missing key {e}")
        return "N/A"

    except Exception as e:
        logger.error(f"Unexpected error fetching rating for {symbol}: {str(e)}", exc_info=True)
        return "N/A"
```

---

## 4. Testing & Diagnostics

### 4.1 Diagnostic Endpoints

**For EVERY major feature, create diagnostic endpoints BEFORE deploying:**

- [ ] **Health Check Endpoint**
  ```python
  @router.get("/health")
  async def health_check():
      """Check if service is running."""
      return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
  ```

- [ ] **Configuration Check**
  ```python
  @router.get("/config-check")
  async def config_check():
      """Check if required environment variables are set."""
      return {
          "database_url_set": bool(os.getenv('DATABASE_URL')),
          "api_key_set": bool(os.getenv('API_KEY')),
          "environment": os.getenv('ENVIRONMENT', 'development')
      }
  ```

- [ ] **Database Diagnostics**
  ```python
  @router.get("/db-check")
  async def db_check(db: Session = Depends(get_db)):
      """Check database connection and table status."""
      try:
          from sqlalchemy import inspect, text
          inspector = inspect(db.bind)

          return {
              "connected": True,
              "tables": inspector.get_table_names(),
              "row_counts": {
                  "users": db.execute(text("SELECT COUNT(*) FROM users")).scalar(),
                  "trades": db.execute(text("SELECT COUNT(*) FROM trades")).scalar()
              }
          }
      except Exception as e:
          return {"connected": False, "error": str(e)}
  ```

- [ ] **Feature-Specific Diagnostics**
  ```python
  @router.get("/check-market-insights")
  async def check_market_insights(db: Session = Depends(get_db)):
      """Check market insights table status and latest data."""
      inspector = inspect(db.bind)
      table_exists = 'market_insights' in inspector.get_table_names()

      result = {
          "table_exists": table_exists,
          "row_count": 0,
          "latest_insight": None
      }

      if table_exists:
          result["row_count"] = db.execute(text("SELECT COUNT(*) FROM market_insights")).scalar()
          latest = db.query(MarketInsight).order_by(MarketInsight.created_at.desc()).first()

          if latest:
              result["latest_insight"] = {
                  "id": latest.id,
                  "created_at": str(latest.created_at),
                  "status": latest.status,
                  "error_message": latest.error_message
              }

      return result
  ```

### 4.2 Manual Testing Endpoints

**Create endpoints to manually trigger operations during development:**

- [ ] **Cache Clear**
  ```python
  @router.post("/clear-cache")
  async def clear_cache():
      """Clear application cache for testing."""
      global _cache
      _cache = {}
      return {"message": "Cache cleared"}
  ```

- [ ] **Manual Triggers**
  ```python
  @router.post("/trigger-scrape")
  async def trigger_scrape():
      """Manually trigger scrape for testing."""
      result = scrape_data()
      return {"message": "Scrape completed", "records": len(result)}
  ```

- [ ] **Database Fixes**
  ```python
  @router.post("/fix-sequences")
  async def fix_sequences(db: Session = Depends(get_db)):
      """Fix PostgreSQL sequences (one-time migration helper)."""
      from sqlalchemy import text

      tables = ['users', 'trades', 'market_insights']
      results = {}

      for table in tables:
          max_id = db.execute(text(f"SELECT MAX(id) FROM {table}")).scalar() or 0
          next_id = max_id + 1
          db.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH {next_id}"))
          results[table] = {"max_id": max_id, "sequence_reset_to": next_id}

      db.commit()
      return {"message": "Sequences fixed", "results": results}
  ```

### 4.3 Test Data Patterns

**For EVERY feature:**

- [ ] **Unit Tests**
  - Test individual functions in isolation
  - Mock external API calls
  - Test edge cases (empty data, null values, errors)
  - Aim for 80%+ code coverage

- [ ] **Integration Tests**
  - Test end-to-end flows
  - Use test database (not production!)
  - Test with real API calls (in CI only)
  - Clean up test data after each test

- [ ] **Load Tests**
  - Test with realistic data volumes
  - Test concurrent requests
  - Measure response times
  - Identify bottlenecks

### 4.4 Monitoring & Alerting

**In production, monitor:**

- [ ] **Application Metrics**
  - Request rates (requests/minute)
  - Response times (p50, p95, p99)
  - Error rates (errors/minute)
  - Cache hit rates

- [ ] **Database Metrics**
  - Query times
  - Connection pool usage
  - Row counts over time
  - Slow query log

- [ ] **External API Metrics**
  - API call counts
  - API error rates
  - Rate limit usage (% of limit)
  - Fallback usage frequency

- [ ] **Alerting Rules**
  - Error rate > 5% for 5 minutes → alert
  - Response time > 2s for 10 minutes → alert
  - Database connections > 80% of pool → alert
  - API rate limit > 90% → alert

---

## 5. Environment & Deployment

### 5.1 Environment Configuration

**Required files in EVERY project:**

- [ ] **`.env` file (local development)**
  ```env
  # Database
  DATABASE_URL=sqlite:///./trading.db

  # APIs
  FINNHUB_API_KEY=your_key_here
  ALPHA_VANTAGE_API_KEY=your_key_here
  PERPLEXITY_API_KEY=your_key_here

  # Application
  ENVIRONMENT=development
  DEBUG=true
  LOG_LEVEL=DEBUG
  ```

- [ ] **`.env.example` file (committed to git)**
  ```env
  # Database
  DATABASE_URL=sqlite:///./trading.db

  # APIs (get keys from respective websites)
  FINNHUB_API_KEY=get_from_finnhub.io
  ALPHA_VANTAGE_API_KEY=get_from_alphavantage.co
  PERPLEXITY_API_KEY=get_from_perplexity.ai

  # Application
  ENVIRONMENT=development
  DEBUG=true
  LOG_LEVEL=DEBUG
  ```

- [ ] **Environment Validation**
  ```python
  # In main.py or __init__.py
  import os
  import logging

  logger = logging.getLogger(__name__)

  # Required environment variables
  REQUIRED_ENV_VARS = [
      'DATABASE_URL',
      'FINNHUB_API_KEY',
  ]

  # Optional environment variables with defaults
  OPTIONAL_ENV_VARS = {
      'LOG_LEVEL': 'INFO',
      'ENVIRONMENT': 'development',
      'DEBUG': 'false',
  }

  def validate_environment():
      """Validate environment variables on startup."""
      missing = []

      for var in REQUIRED_ENV_VARS:
          if not os.getenv(var):
              missing.append(var)

      if missing:
          logger.error(f"Missing required environment variables: {', '.join(missing)}")
          raise EnvironmentError(f"Missing: {', '.join(missing)}")

      # Set defaults for optional vars
      for var, default in OPTIONAL_ENV_VARS.items():
          if not os.getenv(var):
              os.environ[var] = default
              logger.info(f"Using default for {var}: {default}")

      logger.info("✅ Environment validation passed")

  # Call on startup
  validate_environment()
  ```

### 5.2 Local vs. Production Differences

**Always account for these differences:**

| Aspect | Local (Development) | Production (Railway/Heroku/etc.) |
|--------|---------------------|----------------------------------|
| Database | SQLite file | PostgreSQL |
| Environment Variables | `.env` file | Platform dashboard |
| Logging | Console output | Centralized logging |
| Process Isolation | Same process OK | Subprocesses may fail |
| File System | Writable | Ephemeral (files disappear) |
| Networking | No restrictions | Firewall rules |
| Concurrency | Single user | Multiple concurrent users |

**Deployment Checklist:**

- [ ] **Database Migration**
  - Export data from SQLite if needed
  - Import to PostgreSQL
  - Run Alembic migrations
  - Verify schema matches local
  - Check sequences are correct

- [ ] **Environment Variables**
  - Set all required vars in platform dashboard
  - Verify vars are accessible in app (`os.getenv()`)
  - Never commit API keys to git
  - Use platform secrets for sensitive data

- [ ] **File Storage**
  - Don't rely on local file system for persistence
  - Use S3, GCS, or database for file storage
  - Make uploads directory ephemeral-safe

- [ ] **Subprocess Calls**
  - Avoid subprocess calls in production
  - If needed, ensure full environment is passed
  - Test subprocess calls work on platform
  - Consider direct function calls instead

- [ ] **Logging Configuration**
  - Configure logging to stdout (not files)
  - Set appropriate log levels (INFO in prod, DEBUG in dev)
  - Use structured logging (JSON) for parsing
  - Forward logs to monitoring platform

### 5.3 Deployment Process

**Standard deployment flow:**

1. **Local Testing**
   ```bash
   # Run tests
   pytest tests/ -v

   # Run linting
   pylint backend/

   # Check types
   mypy backend/

   # Manual smoke test
   python backend/main.py
   ```

2. **Commit & Push**
   ```bash
   git add .
   git commit -m "Feature: Add X with Y and Z"
   git push origin main
   ```

3. **Automatic Deployment**
   - Railway/Vercel/Heroku auto-deploy from git push
   - Wait 2-3 minutes for deployment
   - Check deployment logs for errors

4. **Post-Deployment Verification**
   ```bash
   # Check health endpoint
   curl https://your-app.railway.app/health

   # Check diagnostics
   curl https://your-app.railway.app/api/diagnostic-endpoint

   # Smoke test critical endpoints
   curl https://your-app.railway.app/api/critical-feature
   ```

5. **Rollback Plan**
   - Keep previous deployment URL if platform supports it
   - Know how to revert git commit
   - Have database backup before major migrations

### 5.4 Never Do This ❌

```python
# ❌ WRONG - Hardcoded API keys
API_KEY = "sk_live_abc123..."  # Never commit this!

# ❌ WRONG - Assuming SQLite in production
DATABASE_URL = "sqlite:///./app.db"  # Breaks in production

# ❌ WRONG - Writing to local filesystem
with open('/tmp/data.json', 'w') as f:  # File disappears on Railway
    json.dump(data, f)

# ❌ WRONG - Subprocess calls without full environment
subprocess.run(['python', 'script.py'])  # Might not have DATABASE_URL

# ❌ WRONG - No validation on startup
app = FastAPI()  # Starts even if DATABASE_URL is missing
```

### 5.5 Do This Instead ✅

```python
# ✅ CORRECT - Environment-based configuration
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file in development

# Get from environment, with validation
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

# Use different config for different environments
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith('sqlite'):
    logger.warning("Using SQLite - OK for development only")
elif DATABASE_URL.startswith('postgresql'):
    logger.info("Using PostgreSQL - production mode")

# Store files in database or cloud storage
def save_file(content: bytes, filename: str):
    """Save file to database instead of filesystem."""
    file_record = FileStorage(
        filename=filename,
        content=content,
        created_at=datetime.utcnow()
    )
    db.add(file_record)
    db.commit()

# Direct function call instead of subprocess
from scheduler.daily_scraper import generate_market_insights
generate_market_insights('manual')  # Same process, same environment
```

---

## 6. Code Organization

### 6.1 Project Structure

**Standard FastAPI + SQLAlchemy structure:**

```
project/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── trades.py
│   │       ├── portfolio.py
│   │       └── daily_brief.py
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   ├── services/
│   │   ├── trade_analyzer.py
│   │   ├── enhanced_options_data.py
│   │   └── recommendation_engine.py
│   ├── scrapers/
│   │   ├── value_trades_scraper.py
│   │   └── google_sheets_scraper.py
│   ├── scheduler/
│   │   └── daily_scraper.py
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_services.py
│   │   └── test_scrapers.py
│   ├── alembic/
│   │   └── versions/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── types/
│   ├── package.json
│   └── next.config.js
├── docs/
│   ├── ERRORS_ENCOUNTERED.md
│   └── BEST_PRACTICES_PRD.md
├── .gitignore
├── README.md
└── docker-compose.yml
```

### 6.2 Separation of Concerns

**Each layer has a specific responsibility:**

- [ ] **Routes (`api/routes/`)** - HTTP request/response handling only
  - Parse request parameters
  - Call service layer
  - Format response
  - Handle HTTP-specific errors (400, 500, etc.)
  - NO business logic
  - NO database queries

- [ ] **Services (`services/`)** - Business logic
  - Implement core features
  - Coordinate between data sources
  - Transform data
  - NO HTTP-specific code
  - NO direct database access (except via models)

- [ ] **Models (`database/models.py`)** - Data access layer
  - Define database schema
  - SQLAlchemy ORM models
  - Basic CRUD operations
  - NO business logic

- [ ] **Scrapers (`scrapers/`)** - External data acquisition
  - Fetch data from external sources
  - Parse HTML/JSON/CSV
  - Return structured data
  - NO database access (return data to caller)

### 6.3 Function Design Principles

**Every function should:**

- [ ] **Single Responsibility** - Do one thing well
- [ ] **Clear Name** - Function name describes what it does
- [ ] **Type Hints** - Use Python type hints for parameters and return values
- [ ] **Docstring** - Explain purpose, parameters, return value, and any side effects
- [ ] **Error Handling** - Handle expected errors, log unexpected ones
- [ ] **Keep It Short** - Aim for < 50 lines per function
- [ ] **Pure When Possible** - Same input → same output (no hidden state)

**Example:**

```python
def calculate_annualized_return(
    premium: float,
    strike: float,
    days_to_expiration: int
) -> float:
    """
    Calculate annualized return for a cash-secured put option.

    Args:
        premium: Option premium received (per share)
        strike: Strike price (per share)
        days_to_expiration: Days until option expires

    Returns:
        Annualized return as percentage (e.g., 25.5 for 25.5%)

    Raises:
        ValueError: If days_to_expiration <= 0

    Example:
        >>> calculate_annualized_return(premium=2.50, strike=100, days_to_expiration=45)
        20.27
    """
    if days_to_expiration <= 0:
        raise ValueError("days_to_expiration must be positive")

    capital_required = strike  # For cash-secured put
    return_for_period = (premium / capital_required) * 100
    annualized = return_for_period * (365 / days_to_expiration)

    return round(annualized, 2)
```

### 6.4 Dependency Management

**For every project:**

- [ ] **requirements.txt** - Pin exact versions
  ```txt
  fastapi==0.104.1
  sqlalchemy==2.0.23
  pydantic==2.5.0
  # NOT: fastapi>=0.100  (unpredictable)
  ```

- [ ] **requirements-dev.txt** - Development dependencies
  ```txt
  pytest==7.4.3
  pytest-cov==4.1.0
  black==23.11.0
  mypy==1.7.1
  pylint==3.0.2
  ```

- [ ] **Update Strategy**
  - Review updates monthly
  - Test in development first
  - Update one major package at a time
  - Check changelog for breaking changes

---

## 7. Performance & Caching

### 7.1 Caching Strategy

**Cache aggressively, invalidate smartly:**

- [ ] **In-Memory Caching**
  ```python
  from datetime import datetime, timedelta

  # Simple in-memory cache
  _cache: Optional[Dict] = None
  _cache_timestamp: Optional[datetime] = None
  _cache_duration = timedelta(minutes=15)

  def get_data():
      global _cache, _cache_timestamp

      # Check cache
      now = datetime.now()
      if _cache and _cache_timestamp:
          if now - _cache_timestamp < _cache_duration:
              logger.info("Returning cached data")
              return _cache

      # Fetch fresh data
      logger.info("Cache miss, fetching fresh data")
      data = expensive_operation()

      # Update cache
      _cache = data
      _cache_timestamp = now

      return data
  ```

- [ ] **Cache Invalidation**
  ```python
  @router.post("/clear-cache")
  async def clear_cache():
      """Manually clear cache when data changes."""
      global _cache, _cache_timestamp
      _cache = None
      _cache_timestamp = None
      return {"message": "Cache cleared"}
  ```

- [ ] **Redis Caching (for production)**
  ```python
  import redis
  import json

  redis_client = redis.Redis(
      host='localhost',
      port=6379,
      decode_responses=True
  )

  def get_data_with_redis(key: str):
      # Try cache
      cached = redis_client.get(key)
      if cached:
          return json.loads(cached)

      # Fetch fresh
      data = expensive_operation()

      # Cache for 15 minutes
      redis_client.setex(key, 900, json.dumps(data))

      return data
  ```

### 7.2 Database Query Optimization

- [ ] **Use Indexes** - Index columns used in WHERE, ORDER BY, JOIN
- [ ] **Avoid N+1 Queries** - Use eager loading (`joinedload`, `selectinload`)
- [ ] **Limit Results** - Always use LIMIT for list endpoints
- [ ] **Paginate** - Implement offset/limit pagination for large datasets
- [ ] **Connection Pooling** - Configure appropriate pool size
- [ ] **Query Monitoring** - Log slow queries (> 1s)

**Example:**
```python
# ❌ WRONG - N+1 query problem
trades = db.query(Trade).all()
for trade in trades:
    symbol = trade.symbol.name  # Additional query for each trade!

# ✅ CORRECT - Eager loading
from sqlalchemy.orm import joinedload

trades = db.query(Trade).options(
    joinedload(Trade.symbol)
).all()
for trade in trades:
    symbol = trade.symbol.name  # No additional queries
```

### 7.3 API Rate Limiting

**Protect external APIs and your own endpoints:**

- [ ] **External API Rate Limits**
  ```python
  from ratelimit import limits, sleep_and_retry

  # Finnhub: 60 calls per minute
  @sleep_and_retry
  @limits(calls=60, period=60)
  def call_finnhub_api(symbol: str):
      """Call Finnhub API with rate limiting."""
      response = requests.get(f"https://finnhub.io/api/...")
      return response.json()
  ```

- [ ] **Internal Rate Limiting**
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address

  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter

  @app.get("/api/expensive-operation")
  @limiter.limit("10/minute")  # Max 10 requests per minute per IP
  async def expensive_operation():
      return perform_expensive_operation()
  ```

### 7.4 Background Jobs

**For long-running operations:**

- [ ] **Scheduled Jobs** - Use APScheduler
  ```python
  from apscheduler.schedulers.background import BackgroundScheduler

  scheduler = BackgroundScheduler()
  scheduler.add_job(
      func=scrape_daily_data,
      trigger='cron',
      hour=7,
      minute=30,
      timezone='America/Los_Angeles'
  )
  scheduler.start()
  ```

- [ ] **Async Tasks** - Use Celery for complex workflows
  ```python
  from celery import Celery

  celery_app = Celery('tasks', broker='redis://localhost:6379')

  @celery_app.task
  def process_large_dataset(dataset_id: int):
      # Long-running task
      pass

  # In API route
  @app.post("/process")
  async def trigger_process(dataset_id: int):
      process_large_dataset.delay(dataset_id)
      return {"message": "Processing started"}
  ```

---

## 8. Documentation Requirements

**Every project must have:**

- [ ] **README.md**
  - Project description
  - Setup instructions
  - Environment variables
  - How to run locally
  - How to deploy
  - Architecture overview

- [ ] **API Documentation**
  - Use FastAPI automatic docs (`/docs` endpoint)
  - Add descriptions to all routes
  - Document request/response schemas
  - Include example requests

- [ ] **Code Comments**
  - Docstrings for all functions/classes
  - Inline comments for complex logic
  - TODOs for future improvements
  - Links to external resources

- [ ] **Architecture Diagrams**
  - System architecture (services, databases, external APIs)
  - Data flow diagrams
  - Database schema (ER diagram)

---

## 9. Security Checklist

- [ ] **Never commit secrets** - Use `.env` files and `.gitignore`
- [ ] **Sanitize user input** - Validate and escape all user-provided data
- [ ] **Use parameterized queries** - Prevent SQL injection
- [ ] **HTTPS only** - Never send sensitive data over HTTP
- [ ] **Authentication** - Implement proper user authentication
- [ ] **Authorization** - Check user permissions for all operations
- [ ] **Rate limiting** - Prevent abuse and DDoS
- [ ] **CORS configuration** - Restrict cross-origin requests appropriately
- [ ] **Dependency scanning** - Use `pip-audit` or Dependabot
- [ ] **Security headers** - Set CSP, X-Frame-Options, etc.

---

## 10. Pre-Deployment Checklist

**Before deploying to production, verify:**

### Code Quality
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Linting clean (`pylint backend/`)
- [ ] Type checking clean (`mypy backend/`)
- [ ] No TODO/FIXME comments for critical features
- [ ] Code reviewed by at least one other developer

### Configuration
- [ ] All environment variables documented in `.env.example`
- [ ] All required environment variables set in production platform
- [ ] Database connection tested
- [ ] External API keys validated

### Database
- [ ] Migrations created (`alembic revision --autogenerate`)
- [ ] Migrations tested locally
- [ ] Migrations applied to staging
- [ ] PostgreSQL sequences checked
- [ ] Backup created before major schema changes

### Monitoring
- [ ] Health check endpoint working (`/health`)
- [ ] Diagnostic endpoints working
- [ ] Logging configured correctly
- [ ] Error tracking set up (Sentry, etc.)
- [ ] Alerting rules configured

### Documentation
- [ ] README.md updated
- [ ] API documentation current
- [ ] Architecture diagrams updated
- [ ] Deployment instructions tested

### Testing
- [ ] Manual smoke test passed
- [ ] Load test passed (if applicable)
- [ ] Integration tests passed
- [ ] Rollback plan documented

---

## Appendix A: Common Antipatterns

### Antipattern 1: God Object
**Problem:** One class/file does everything.

**Solution:** Split into focused, single-responsibility modules.

### Antipattern 2: Magic Numbers
**Problem:** Hardcoded values without explanation.
```python
if score > 0.75:  # What does 0.75 mean?
```

**Solution:** Use named constants.
```python
HIGH_PRIORITY_THRESHOLD = 0.75  # Trades scoring above this are high priority
if score > HIGH_PRIORITY_THRESHOLD:
```

### Antipattern 3: Tight Coupling
**Problem:** Modules depend on each other's internals.

**Solution:** Use interfaces/abstract classes, dependency injection.

### Antipattern 4: Premature Optimization
**Problem:** Optimizing before measuring.

**Solution:** Profile first, optimize bottlenecks only.

### Antipattern 5: Copy-Paste Programming
**Problem:** Duplicating code instead of abstracting.

**Solution:** Extract common functionality into reusable functions.

---

## Appendix B: Tool Recommendations

### Development Tools
- **IDE:** VS Code with Python extensions
- **Linting:** pylint, flake8, black (auto-formatting)
- **Type Checking:** mypy
- **Testing:** pytest, pytest-cov
- **API Testing:** Postman, HTTPie

### Deployment Tools
- **Hosting:** Railway (backend), Vercel (frontend)
- **Database:** PostgreSQL (production), SQLite (development)
- **Migrations:** Alembic
- **Monitoring:** Sentry (errors), Datadog (metrics)

### External APIs
- **Stock Data:** Finnhub, Alpha Vantage, yfinance (fallback)
- **AI:** Perplexity AI, OpenAI
- **Caching:** Redis
- **Task Queue:** Celery + Redis

---

## Version History

- **1.0** (2025-10-31) - Initial version based on Options Trading Platform errors

---

## How to Use This PRD

1. **Before starting a new feature:**
   - Read relevant sections
   - Check off applicable items
   - Design with these principles in mind

2. **During code review:**
   - Use as a checklist
   - Reference specific sections in review comments
   - Update PRD if new patterns emerge

3. **Before deployment:**
   - Complete "Pre-Deployment Checklist"
   - Verify all critical items checked
   - Document any exceptions with reasoning

4. **After incidents:**
   - Document new error patterns in ERRORS_ENCOUNTERED.md
   - Update this PRD with new best practices
   - Share learnings with team

---

**Remember:** This is a living document. Update it as you learn new patterns and encounter new problems.
