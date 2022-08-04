import email
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, session, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spend.db'
db = SQLAlchemy(app)


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


class Article(db.Model):
    """
    Создаю БД для внесения продуктов и их цен
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Integer)

    def __repr__(self) -> str:
        return '<Article %r>' % self.id

# функция входа
    @app.route('/sign_in')
    def sign_in():
        return render_template("sign_in.html")


# функция основной страницы


    @app.route('/')
    def index():
        article = Article.query.order_by(Article.date.desc()).all()
        return render_template("index.html", article=article)

# сраница вода данных

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

    # Редактирование трат

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
