from flask import Flask, render_template, redirect, jsonify, make_response, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import abort
from data import db_session
from data.users import Users
from data.register import RegisterForm, LoginForm
from data.questions import Questions, QuestionsForm
from data.answers import Answers, AnswersForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_super_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init('db/info.sqlite')
    app.run()


@app.route('/')
def index():
    session = db_session.create_session()
    if current_user.is_authenticated:
        questions = session.query(Questions).filter(Questions.user == current_user)
    else:
        questions = session.query(Questions)

    return render_template("index.html", questions=questions)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = Users(
            email=form.email.data,
            name=form.name.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(Users).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/create_question',  methods=['GET', 'POST'])
@login_required
def create_question():
    form = QuestionsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        question = Questions()
        question.theme = form.theme.data
        question.content = form.content.data
        current_user.questions.append(question)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('questions.html', title='Добавление вопроса',
                           form=form)


@app.route('/edit_question/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_question(id):
    form = QuestionsForm()
    if request.method == "GET":
        session = db_session.create_session()
        question = session.query(Questions).filter(Questions.id == id,
                                          Questions.user == current_user).first()
        if question:
            form.theme.data = question.theme
            form.content.data = question.content
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        question = session.query(Questions).filter(Questions.id == id,
                                          Questions.user == current_user).first()
        if question:
            question.theme = form.theme.data
            question.content = form.content.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('questions.html', title='Редактирование вопроса', form=form)
#
#
@app.route('/question_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def question_delete(id):
    session = db_session.create_session()
    question = session.query(Questions).filter(Questions.id == id,
                                      Questions.user == current_user).first()
    if question:
        session.delete(question)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/question_page/<int:id>', methods=['GET', 'POST'])  # страница с вопросом и ответами
@login_required
def question_page(id):
    form = AnswersForm()
    session = db_session.create_session()
    question = session.query(Questions).filter(Questions.id == id).first()
    if question:
        user = session.query(Users).filter(Users.id == question.user_id).first()  # юзер, задавший вопрос
    else:
        abort(404)

    if form.validate_on_submit():
        session = db_session.create_session()
        question = session.query(Questions).filter(Questions.id == id).first()
        user = session.query(Users).filter(Users.id == question.user_id).first()  # юзер, задавший вопрос

        answer = Answers()
        answer.content = form.content.data
        answer.question_id = id
        current_user.answers.append(answer)
        session.merge(current_user)
        session.commit()
        form.content.data = ''

    return render_template('question_page.html', question=question, user=user, form=form)


@app.route('/delete_answer/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_answer(id):
    session = db_session.create_session()
    answer = session.query(Answers).filter(Answers.id == id, Answers.user == current_user).first()
    if answer:
        session.delete(answer)
        session.commit()
    else:
        abort(404)
    return redirect('/')


# @app.route('/create_answer', methods=['GET', 'POST'])
# @login_required
# def create_answer():
#     form = AnswersForm()
#     if form.validate_on_submit():
#         session = db_session.create_session()
#         answer = Answers()
#         answer.content = form.content.data
#         current_user.answers.append(answer)
#         session.merge(current_user)
#         session.commit()
#         return redirect('/')


@app.errorhandler(404)
def not_found(error):
    form = QuestionsForm()
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
