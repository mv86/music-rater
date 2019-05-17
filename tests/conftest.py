from pathlib import Path

from alembic.command import downgrade, upgrade
from alembic.config import Config

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


TEST_DB = 'test.db'
TEST_DB_PATH = Path.cwd() / TEST_DB
TEST_DATABASE_URI = f'sqlite:///{TEST_DB_PATH}'
ALEMBIC_CONFIG = Path.cwd() / 'alembic.ini'


def apply_migrations():
    """Applies all alembic migrations for testing session"""
    config = Config(ALEMBIC_CONFIG)
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URI)
    upgrade(config, 'head')


def downgrade_migrations():
    """Downgrades all alembic migrations for testing session"""
    config = Config(ALEMBIC_CONFIG)
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URI)
    downgrade(config, 'base')


@pytest.fixture(scope='session')
def test_engine():
    """Creates a DB engine for a testing session"""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    test_engine = create_engine(TEST_DATABASE_URI)
    apply_migrations()

    yield test_engine

    downgrade_migrations()
    TEST_DB_PATH.unlink()


@pytest.fixture(scope='function')
def test_session(test_engine):
    """Creates a new database session for a test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    test_db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=test_engine))

    yield test_db_session

    transaction.rollback()
    connection.close()
    test_db_session.remove()