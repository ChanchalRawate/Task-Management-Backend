import pytest
from app.app import create_app
from app.extensions import db
from app.models.user import User
from app.models.task import Task
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            user = User(email="taskuser@example.com", password_hash=generate_password_hash("pass"))
            db.session.add(user)
            db.session.commit()
            token = create_access_token(identity=user.id)
            client.token = token
            client.user_id = user.id
        yield client

def test_create_task(client):
    response = client.post(
        "/tasks/",
        headers={"Authorization": f"Bearer {client.token}"},
        json={"title": "Test Task", "description": "Task Desc"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["msg"] == "Task created"

def test_get_tasks(client):
    # create a task first
    task = Task(title="Fetch Task", owner_id=client.user_id)
    db.session.add(task)
    db.session.commit()

    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {client.token}"}
    )
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Fetch Task"
