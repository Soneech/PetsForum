import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import BooleanField, SubmitField, StringField, TextAreaField

from .db_session import SqlAlchemyBase


class Questions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    theme = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    # is_published = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('Users')


class QuestionsForm(FlaskForm, SerializerMixin):
    theme = StringField('Тема', validators=[DataRequired()])
    content = TextAreaField("Вопрос")
    is_private = BooleanField("Личное")
    submit = SubmitField('Опубликовать')
