import pytest

from sqlalchemy import create_engine
from cosmicpython.orm import mapper_registry, sessionmaker, clear_mappers

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
