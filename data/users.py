import sqlalchemy
import hashlib
from . import db_session
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_questions = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user_answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    # jobs = orm.relation('Jobs', back_populates='user')
    questions = orm.relation("Questions", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
        # self.hashed_password = hashlib.md5(password.encode()).hexdigest()

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
