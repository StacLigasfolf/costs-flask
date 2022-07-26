from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spend.db'
db = SQLAlchemy(app)


class Article(db.Model):
    """
    Создаю БД для внесения продукта и его цены
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Integer)

    def __repr__(self) -> str:
        return '<Article %r>' % self.id

# функция основной страницы


@app.route('/')
def index():
    return render_template("index.html")

# функция страницы в которой вводят данные о продукте и его цене


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
        return render_template("input.html")

# форма вывода внесенных данных


@app.route("/spending")
def spending():
    article = Article.query.order_by(Article.date.desc()).all()
    return render_template("spending.html", article=article)

# страница пользователя


@app.route('/user/<string:name>/<int:id>')
def user(name='Mark', id=2):
    return render_template("user.html")


if __name__ == "__main__":
    app.run(debug=True)
