from flask_wtf import FlaskForm
from sqlalchemy_serializer import SerializerMixin
from wtforms import StringField, SubmitField


class SearchForm(FlaskForm, SerializerMixin):
    content = StringField('Поиск')
    submit = SubmitField('Искать')