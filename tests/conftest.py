# tests/conftest.py
import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



@pytest.fixture
def client():
    with app.test_client() as client:
        yield client