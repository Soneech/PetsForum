import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, TextAreaField

from .db_session import SqlAlchemyBase


class Messages(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    to_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    from_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    dialog = orm.relation('DialogsInfo')


class MessageForm(FlaskForm, SerializerMixin):
    content = TextAreaField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить', validators=[DataRequired()])
