"""Initialize database tables"""
from .connection import engine, Base
from . import models

def init_db():
    """Create all database tables"""
    # Import all models to ensure they're registered with Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
