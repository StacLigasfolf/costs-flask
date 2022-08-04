from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, session, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import json

app = Flask(__name__)
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


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<profiles {self.id}>"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Integer)

    def __repr__(self) -> str:
        return '<Article %r>' % self.id


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
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
        return redirect('sign_in')
    return render_template("registration.html")


# функция входа

@app.route('/sign_in')
def sign_in():
    return render_template("sign_in.html")


# функция основной страницы

@app.route('/')
def index():
    article = Article.query.order_by(Article.date.desc()).all()
    return render_template("index.html", article=article)

# сраница ввода данных


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


@app.route("/spending")
def spending():
    article = Article.query.order_by(Article.date.desc()).all()
    return render_template("spending.html", article=article)

# Удаление записи


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


@app.route("/indicators")
def indicators():
    return render_template("indicators.html")

# страница пользователя


@app.route('/user/<string:name>/<int:id>')
def user(name='Mark', id=2):
    return render_template("user.html")


if __name__ == "__main__":
    app.run(debug=True)
