from ..models.user import User
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(email, password):
    if User.query.filter_by(email=email).first():
        return None
    hashed_pw = generate_password_hash(password)
    user = User(email=email, password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return user

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
