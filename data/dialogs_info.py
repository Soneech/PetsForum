import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class DialogsInfo(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'dialogs_info'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id_1 = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id_2 = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_name_1 = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_name_2 = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    messages = orm.relation('Messages', back_populates='dialog')
