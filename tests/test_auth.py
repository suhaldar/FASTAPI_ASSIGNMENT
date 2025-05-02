import pytest
from fastapi import status

def test_login_missing_credentials(client):
    """Test login with missing credentials."""
    response = client.post("/login", data={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 