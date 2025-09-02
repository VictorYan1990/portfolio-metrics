from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Database configuration template
DB_CONFIG_TEMPLATE = {
    'user': 'postgres',  # Replace with your PostgreSQL username
    'password': '1990',  # Replace with your PostgreSQL password
    'host': 'localhost',
    'port': 5432
}


# Utility function to generate the database URL
def get_database_url(database_name):
    return (
        f"postgresql+psycopg2://{DB_CONFIG_TEMPLATE['user']}:{DB_CONFIG_TEMPLATE['password']}@"
        f"{DB_CONFIG_TEMPLATE['host']}:{DB_CONFIG_TEMPLATE['port']}/{database_name}"
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
        logging.debug(f"Database connection established for {database_name}")
        yield db
    finally:
        logging.debug(f"Closing database connection for {database_name}")
        db.close()


# Test connection
if __name__ == "__main__":
    try:
        with get_engine('user_data').connect() as connection:
            logging.info("Successfully connected to the database user_data.")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
