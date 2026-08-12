from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
from app.config import settings

# Determine if the DB is SQLite to apply special connect args
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True
)

# SessionLocal is used to instantiate db sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Standard base class for models
class Base(DeclarativeBase):
    pass

# DB Dependency injection helper for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
