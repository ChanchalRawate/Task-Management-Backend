import pytest
from app.app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Pre-create a user
            user = User(email="test@example.com", password_hash=generate_password_hash("password"))
            db.session.add(user)
            db.session.commit()
        yield client

def test_register(client):
    response = client.post("/auth/register", json={"email": "new@example.com", "password": "123456"})
    assert response.status_code == 201
    assert b"User created" in response.data

def test_login_success(client):
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_login_fail(client):
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "wrong"})
    assert response.status_code == 401
