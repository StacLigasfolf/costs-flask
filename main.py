from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, session, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime


app = Flask(__name__)
app.secret_key = 'L1gas'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spend.db'
db = SQLAlchemy(app)


manager = LoginManager(app)

'''
    Здесь написаны классы, с помощю которых создаются таблицы для БД SQLALchemy
    return:
        class Users - пользователи 
        class Profile - профиль пользователя содержащий только имя и связан с ним
        class Article - таблица для внесения данных о продукте и их цен
'''


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    psw = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # data_id = db.Column(db.Integer, db.ForeignKey('article.id'))

    def __repr__(self):
        return f"<profiles {self.id}>"



class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Integer)

    def __repr__(self) -> str:
        return '<article %r>' % self.id

with app.app_context():
    db.create_all()
    print("Все таблицы созданы!")  # Для проверки
'''
    Тут начинаются функции воспроизведения страниц и их взаимодействиями с SQLALchemy
    return:
        # функция регистрации
        # функция входа
        # сраница ввода данных
        # Удаление записи
        # Редактирование записи
        # получение и обработка данных
        # страница пользователя
'''


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('/sign_in'))
    return response

# функция регистрации


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        # здесь должна быть проверка корректности введенных данных
        try:
            hash = generate_password_hash(request.form['psw'])
            u = Users(email=request.form['email'], psw=hash)
            db.session.add(u)

            p = Profiles(name=request.form['name'], user_id=u.id)
            db.session.add(p)
            db.session.commit()
            return redirect('/sign_in')
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
        return redirect('/sign_in')
    return render_template("registration.html")


# функция входа
@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    login = request.form.get('email')
    password = request.form.get('psw')

    if login and password:
        user = Users.query.filter_by(email=login).first()
        if user and check_password_hash(user.psw, password):
            login_user(user)

            return redirect('/')
        else:
            flash('Проверьте логин или пароль')
    else:
        flash('Пожалуйста, авторизуйтесь')
    return render_template("sign_in.html")


# функция выхода из учетной записи
@app.route('/sign_out', methods=['POST', 'GET'])
def sign_out():
    logout_user()
    return redirect('/sign_in')

    # функция основной страницы


@login_required
@app.route('/')
def index():
    article = Article.query.order_by(Article.date.desc()).all()
    return render_template("index.html", article=article)

# сраница ввода данных


@login_required
@app.route('/input', methods=['POST', 'GET'])
def input():
    if request.method == "POST":
        product = request.form['product']
        price = request.form['price']

        article = Article(product=product, price=price)

        try:
            db.session.add(article)
            db.session.commit()

            return redirect('/input')

        except:
            return 'какая-то ошибка'

    else:
        article = Article.query.order_by(Article.date.desc()).all()
        return render_template("input.html", article=article)

# форма вывода внесенных данных


@login_required
@app.route("/spending")
def spending():
    article = Article.query.order_by(Article.date.desc()).all()
    return render_template("spending.html", article=article)

# Удаление записи


@login_required
@app.route("/spending/<int:id>/del")
def spending_delete(id):
    article = Article.query.get(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/')
    except:
        return "ОЙ, ЧТО-ТО ПОШЛО НЕ ТАК"

# Редактирование записи


@login_required
@app.route("/refactor/<int:id>/update", methods=['POST', 'GET'])
def spending_update(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.product = request.form['product']
        article.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/spending')
        except:
            return 'При редактировании траты, произошла ошибка'
    else:
        return render_template("refactor.html", article=article)

# получение и обработка данных


@login_required
@app.route("/indicators")
def indicators():
    return render_template("indicators.html")

# страница пользователя


@login_required
@app.route('/user/<string:name>/<int:id>')
def user(name='Mark', id=2):
    return render_template("user.html")


if __name__ == "__main__":
    app.run(debug=True)
