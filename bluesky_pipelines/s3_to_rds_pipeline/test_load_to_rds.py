"""Tests for load script"""
import sqlalchemy
from load_to_rds import DBLoader


def test_get_engine_returns_engine():
    """Test if get_engine returns as expected."""
    loader = DBLoader()
    eng = loader.get_sql_conn()
    assert isinstance(eng, sqlalchemy.engine.Engine)
