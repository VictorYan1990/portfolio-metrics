from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.util.logger import logger
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Database configuration from environment variables
# No defaults for sensitive values - must be provided via environment variables
DB_CONFIG_TEMPLATE = {
    'user': os.getenv('DB_USER', 'postgres'),  # Defaults to 'postgres' if not set
    'password': os.getenv('DB_PASSWORD'),  # REQUIRED - no default for security
    'host': os.getenv('DB_HOST', 'localhost'),  # Defaults to 'localhost' for local dev
    'port': int(os.getenv('DB_PORT', '5432'))  # Defaults to 5432 if not set
}


# Utility function to generate the database URL
def get_database_url(database_name):
    """Generate database URL from configuration. Raises error if password not set."""
    if not DB_CONFIG_TEMPLATE['password']:
        raise ValueError("DB_PASSWORD environment variable is required")
    
    # Add SSL mode for managed services (can be overridden)
    ssl_mode = os.getenv('DB_SSLMODE', 'prefer')
    
    return (
        f"postgresql+psycopg2://{DB_CONFIG_TEMPLATE['user']}:{DB_CONFIG_TEMPLATE['password']}@"
        f"{DB_CONFIG_TEMPLATE['host']}:{DB_CONFIG_TEMPLATE['port']}/{database_name}"
        f"?sslmode={ssl_mode}"
    )


# Connection pool manager
engines = {}  # Cache for database engines


def get_engine(database_name):
    """Get or create an engine for the specified database."""
    if database_name not in engines:
        engines[database_name] = create_engine(
            get_database_url(database_name),
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            future=True  # Enables modern SQLAlchemy 1.4+ behavior
        )
    return engines[database_name]


# Session factory
def get_db(database_name):
    """Provide a session for the specified database."""
    engine = get_engine(database_name)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        logger.info(f"Database connection established for {database_name}")
        yield db
    finally:
        logger.info(f"Closing database connection for {database_name}")
        db.close()


# Test connection
if __name__ == "__main__":
    try:
        with get_engine('user_data').connect() as connection:
            logger.info("Successfully connected to the database user_data.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
