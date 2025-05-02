import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.utils.security import create_access_token

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite://"  # in-memory database

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    from app.models.user import User
    user = User(
        username="testuser",
        email="test@example.com",
        password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LcdYIdQGwQ05gXQ5i",  # password: test123
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_admin(db_session):
    from app.models.user import User
    admin = User(
        username="testadmin",
        email="admin@example.com",
        password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LcdYIdQGwQ05gXQ5i",  # password: test123
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def user_token(test_user):
    return create_access_token(data={"sub": test_user.username})

@pytest.fixture
def admin_token(test_admin):
    return create_access_token(data={"sub": test_admin.username}) 