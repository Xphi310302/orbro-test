from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

# Create async engine
DATABASE_URL = "sqlite+aiosqlite:///./jobs.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create declarative base
Base = declarative_base()


# Table schema for the database
class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    count = Column(Integer, default=0)
    img = Column(String)  # Path to the image file
    created = Column(DateTime, default=datetime.now().astimezone())


# Database initialization function
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Get database session
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
