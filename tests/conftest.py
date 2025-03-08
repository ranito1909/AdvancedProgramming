# tests/conftest.py
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def pytest_configure(config):
    config.addinivalue_line("markers", "regression: mark test as regression")
