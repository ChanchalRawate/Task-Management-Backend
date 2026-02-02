from ..extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks_owned = db.relationship("Task", backref="owner", foreign_keys="Task.owner_id")
    tasks_assigned = db.relationship("Task", backref="assignee", foreign_keys="Task.assigned_to")
