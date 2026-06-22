from database import db
from models.user import User


class UserRepository:
    """Isola o acesso a dados de User."""

    def get_all(self):
        return User.query.all()

    def get_by_id(self, user_id):
        return db.session.get(User, user_id)

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def count(self):
        return User.query.count()

    def add(self, user):
        db.session.add(user)

    def delete(self, user):
        db.session.delete(user)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
