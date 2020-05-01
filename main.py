from flask import Flask, render_template, redirect, jsonify, make_response, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import abort
from data import db_session
from data.users import Users
from data.register import RegisterForm, LoginForm
from data.questions import Questions, QuestionsForm
from data.answers import Answers, AnswersForm
from data.search_form import SearchForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_super_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init('db/info.sqlite')
    app.run()


@app.route('/', methods=['GET', 'POST'])
def index():
    session = db_session.create_session()
    questions = list(session.query(Questions))
    questions.reverse()  # "сортировка" вопросов по дате написания (сначала самые новые)
    form = SearchForm()
    if form.validate_on_submit():  # поиск вопроса
        req = form.content.data.lower()
        form.content.data = ''
        # вопросы, удовлетворяющие поисковому запросу
        questions = [q for q in questions if req in q.content.lower() or req in q.theme.lower()]

    return render_template("index.html", questions=questions, form=form)


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

        if current_user.user_questions:  # обновление кол-ва заданных вопросов
            current_user.user_questions += 1
        else:
            current_user.user_questions = 1
        print(current_user.user_questions)

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


@app.route('/delete_question/<int:id>', methods=['GET', 'POST'])
@login_required
def question_delete(id):
    session = db_session.create_session()
    question = session.query(Questions).filter(Questions.id == id,
                                      Questions.user == current_user).first()
    if question:
        answers = session.query(Answers).filter(Answers.question_id == id)
        for item in answers:
            session.delete(item)
        session.delete(question)
        session.commit()
    else:
        abort(404)
    return redirect('/')


# страница с вопросом и ответами (здесь также реализовано создание ответа)
@app.route('/question_page/<int:id>', methods=['GET', 'POST'])
def question_page(id):
    form = AnswersForm()
    session = db_session.create_session()
    question = session.query(Questions).filter(Questions.id == id).first()
    answers = session.query(Answers).filter(Answers.question_id == id)
    if question:
        user = session.query(Users).filter(Users.id == question.user_id).first()  # юзер, задавший вопрос
    else:
        abort(404)

    if form.validate_on_submit():
        session = db_session.create_session()
        question = session.query(Questions).filter(Questions.id == id).first()

        answer = Answers()
        answer.content = form.content.data
        answer.question_id = id
        current_user.answers.append(answer)
        if current_user.user_answers:  # обновление кол-ва ответов
            current_user.user_answers += 1
        else:
            current_user.user_answers = 1

        session.merge(current_user)
        session.commit()
        form.content.data = ''

    return render_template('question_page.html', question=question,
                           answers=answers, user=user, form=form)


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


@app.route('/edit_answer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_answer(id):
    form = AnswersForm()
    session = db_session.create_session()
    answer = session.query(Answers).filter(Answers.id == id,
                                           Answers.user_id == current_user.id).first()
    if answer:
        if request.method == 'GET':
            form.content.data = answer.content
        if form.validate_on_submit():
            answer.content = form.content.data
            form.content.data = ''
            session.commit()
    else:
        abort(404)

    question = session.query(Questions).filter(Questions.id == answer.question_id).first()
    answers = session.query(Answers).filter(Answers.question_id == answer.question_id)
    user = session.query(Users).filter(Users.id == question.user_id).first()
    return render_template('question_page.html', question=question,
                           answers=answers, user=user, form=form)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
