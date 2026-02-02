from ..models.task import Task
from ..extensions import db

def create_task(owner_id, title, description, assigned_to=None, status="TODO", priority="MEDIUM", due_date=None):
    task = Task(
        title=title,
        description=description,
        owner_id=owner_id,
        assigned_to=assigned_to,
        status=status,
        priority=priority,
        due_date=due_date
    )
    db.session.add(task)
    db.session.commit()
    return task

def get_tasks(user_id, page=1, limit=10, status=None):
    query = Task.query.filter(
        (Task.owner_id==user_id) | (Task.assigned_to==user_id)
    )
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Task.created_at.desc()).paginate(page, limit, False)

def update_task(task, **kwargs):
    for key, value in kwargs.items():
        setattr(task, key, value)
    db.session.commit()
    return task

def delete_task(task):
    db.session.delete(task)
    db.session.commit()
