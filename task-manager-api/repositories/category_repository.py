from database import db
from models.category import Category


class CategoryRepository:
    """Isola o acesso a dados de Category."""

    def get_all(self):
        return Category.query.all()

    def get_by_id(self, category_id):
        return db.session.get(Category, category_id)

    def count(self):
        return Category.query.count()

    def add(self, category):
        db.session.add(category)

    def delete(self, category):
        db.session.delete(category)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
