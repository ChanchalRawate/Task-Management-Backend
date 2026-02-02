from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.task import Task
from ..extensions import db

task_bp = Blueprint("task", __name__)

@task_bp.route("/", methods=["GET"])
@jwt_required()
def get_tasks():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    status = request.args.get("status")

    query = Task.query
    if status:
        query = query.filter_by(status=status)

    tasks = query.paginate(page=page, per_page=limit).items
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "priority": t.priority,
        "due_date": t.due_date,
        "owner_id": t.owner_id,
        "assigned_to": t.assigned_to
    } for t in tasks])

@task_bp.route("/", methods=["POST"])
@jwt_required()
def create_task():
    data = request.get_json()
    user_id = get_jwt_identity()
    task = Task(
        title=data.get("title"),
        description=data.get("description"),
        owner_id=user_id,
        assigned_to=data.get("assigned_to"),
        status=data.get("status", "TODO"),
        priority=data.get("priority", "MEDIUM")
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"msg": "Task created", "id": task.id}), 201

@task_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    for key in ["title", "description", "status", "priority", "assigned_to"]:
        if key in data:
            setattr(task, key, data[key])
    db.session.commit()
    return jsonify({"msg": "Task updated"})

@task_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"msg": "Task deleted"})
