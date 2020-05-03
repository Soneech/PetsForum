import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, StringField, TextAreaField

from .db_session import SqlAlchemyBase


class Questions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    theme = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=datetime.datetime.today().strftime('%d.%m.%Y, %H:%M'))

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('Users')

    answers = orm.relation('Answers', back_populates='question')


class QuestionsForm(FlaskForm, SerializerMixin):
    theme = StringField('Тема', validators=[DataRequired()])
    content = TextAreaField('Вопрос', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
