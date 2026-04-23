"""SQLAlchemy datubāzes savienojums un sesijas."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


# SQLite prasa šo karogu, ja sesija tiek izmantota ārpus galvenā stapu
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    """FastAPI dependency, kas atdod datu bāzes sesiju."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Izveido tabulas, ja to nav."""
    # Importē modeļus, lai tie tiktu reģistrēti uz Base metadata
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
