"""
Database Connection Template
Handles SQLite (development) and PostgreSQL (production)
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

# ✅ CRITICAL: Only load .env if DATABASE_URL not already set by platform
# Railway/Vercel inject environment variables - don't override them!
if not os.getenv('DATABASE_URL'):
    load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. "
        "Set it in .env for local development or platform dashboard for production."
    )

# ============================================================================
# ENGINE CONFIGURATION
# ============================================================================

# SQLite configuration (development only)
if DATABASE_URL.startswith('sqlite'):
    print("⚠️  Using SQLite - FOR DEVELOPMENT ONLY!")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True to see SQL queries
    )

# PostgreSQL configuration (production)
else:
    print("✅ Using PostgreSQL - Production configuration")
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,  # Number of permanent connections
        max_overflow=10,  # Number of additional connections when pool is full
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False,  # Set to True to see SQL queries
    )

# ============================================================================
# SESSION CONFIGURATION
# ============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db():
    """
    FastAPI dependency that provides a database session.

    Usage:
        @app.get("/api/data")
        async def get_data(db: Session = Depends(get_db)):
            return db.query(MyModel).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def create_tables():
    """Create all tables defined in models"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

def drop_tables():
    """Drop all tables (USE WITH CAUTION!)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped")

def fix_sequence(table_name: str, db_session):
    """
    Fix PostgreSQL sequence after manual data insertion.

    Args:
        table_name: Name of the table
        db_session: SQLAlchemy session

    Usage:
        with SessionLocal() as db:
            fix_sequence('users', db)
    """
    if not DATABASE_URL.startswith('postgresql'):
        print("⚠️  Sequence fix only needed for PostgreSQL")
        return

    try:
        # Get max ID from table
        max_id = db_session.execute(
            text(f"SELECT MAX(id) FROM {table_name}")
        ).scalar() or 0

        # Reset sequence to max_id + 1
        db_session.execute(
            text(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH {max_id + 1}")
        )
        db_session.commit()

        print(f"✅ Fixed sequence for {table_name} (restarted at {max_id + 1})")
    except Exception as e:
        print(f"❌ Error fixing sequence for {table_name}: {e}")
        db_session.rollback()

def check_connection():
    """
    Check if database connection is working.
    Returns True if connected, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# ============================================================================
# INITIALIZATION
# ============================================================================

# Verify connection on import
if __name__ == "__main__":
    check_connection()
    print(f"Database URL: {DATABASE_URL[:30]}...")  # Don't print full URL
