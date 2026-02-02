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
