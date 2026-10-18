import pytest
import auth


@pytest.fixture(autouse=True)
def fresh_store():
    """Give every test a clean in-memory store."""
    auth.initialize_store()
