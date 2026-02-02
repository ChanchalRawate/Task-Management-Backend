# ----------------------------
# PowerShell Script: setup-backend.ps1
# ----------------------------

# 1️⃣ Create folder structure
$folders = @(
    "app",
    "app\models",
    "app\routes",
    "app\utils"
)

foreach ($f in $folders) {
    if (-not (Test-Path $f)) { New-Item -ItemType Directory -Path $f }
}

# 2️⃣ Create files
$files = @(
    "app\__init__.py",
    "app\config.py",
    "app\extensions.py",
    "app\models\user.py",
    "app\models\task.py",
    "app\routes\auth_routes.py",
    "app\routes\task_routes.py",
    "app\utils\decorators.py",
    "run.py",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "README.md"
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) { New-Item -ItemType File -Path $file }
}

# 3️⃣ Populate requirements.txt
$reqs = @"
flask
flask-sqlalchemy
flask-jwt-extended
pymysql
python-dotenv
werkzeug
"@
Set-Content -Path "requirements.txt" -Value $reqs

# 4️⃣ Populate app/config.py
$config = @"
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:root@mysql:3306/taskdb'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-key'
"@
Set-Content -Path "app\config.py" -Value $config

# 5️⃣ Populate app/extensions.py
$ext = @"
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
"@
Set-Content -Path "app\extensions.py" -Value $ext

# 6️⃣ Populate app/__init__.py
$init = @"
from flask import Flask
from .config import Config
from .extensions import db, jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from .routes.auth_routes import auth_bp
    from .routes.task_routes import task_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')

    return app
"@
Set-Content -Path "app\__init__.py" -Value $init

# 7️⃣ Populate app/models/user.py
$userModel = @"
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
"@
Set-Content -Path "app\models\user.py" -Value $userModel

# 8️⃣ Populate app/models/task.py
$taskModel = @"
from app.extensions import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='TODO')
    priority = db.Column(db.String(20), default='MEDIUM')

    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"@
Set-Content -Path "app\models\task.py" -Value $taskModel

# 9️⃣ Populate app/routes/auth_routes.py
$authRoutes = @"
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(message='User registered'), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify(error='Invalid credentials'), 401

    token = create_access_token(identity=user.id)
    return jsonify(access_token=token)
"@
Set-Content -Path "app\routes\auth_routes.py" -Value $authRoutes

# 10️⃣ Populate app/routes/task_routes.py
$taskRoutes = @"
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.task import Task

task_bp = Blueprint('tasks', __name__)

@task_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.json

    task = Task(
        title=data['title'],
        description=data.get('description'),
        priority=data.get('priority', 'MEDIUM'),
        created_by=user_id,
        assigned_to=data.get('assigned_to')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(message='Task created'), 201

@task_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    tasks = Task.query.paginate(page=page, per_page=limit, error_out=False)
    return jsonify([
        {
            'id': t.id,
            'title': t.title,
            'status': t.status,
            'priority': t.priority
        } for t in tasks.items
    ])
"@
Set-Content -Path "app\routes\task_routes.py" -Value $taskRoutes

# 11️⃣ Populate run.py
$runPy = @"
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"@
Set-Content -Path "run.py" -Value $runPy

# 12️⃣ Populate Dockerfile
$dockerfile = @"
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ['python', 'run.py']
"@
Set-Content -Path "Dockerfile" -Value $dockerfile

# 13️⃣ Populate docker-compose.yml
$dockerCompose = @"
services:
  backend:
    build: .
    ports:
      - '5000:5000'
    depends_on:
      - mysql

  mysql:
    image: mysql:8
    environment:
      MYSQL_DATABASE: taskdb
      MYSQL_ROOT_PASSWORD: root
    ports:
      - '3306:3306'
"@
Set-Content -Path "docker-compose.yml" -Value $dockerCompose

# 14️⃣ Populate README.md
$readme = @"
Task Manager Backend - Flask + MySQL + JWT
"@
Set-Content -Path "README.md" -Value $readme

Write-Host "✅ Project structure created successfully!"
