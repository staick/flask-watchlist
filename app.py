import os
import sys
import click
from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape


WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = prefix + os.path.join(app.root_path, "data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app


class User(db.Model):  # 表名将会是 user (自动生成，小写处理)
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))


class Movie(db.Model):  # 表名将会是movie
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option("--drop", is_flag=True, help="Create after drop.")  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialize database.")


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    name = "Grey Li"
    movies = [
        {"title": "My Neighbor Totoro", "year": "1988"},
        {"title": "Dead Poets Society", "year": "1989"},
        {"title": "A Perfect World", "year": "1993"},
        {"title": "Leon", "year": "1994"},
        {"title": "Mahjong", "year": "1996"},
        {"title": "Swallowtail Butterfly", "year": "1996"},
        {"title": "King of Comedy", "year": "1999"},
        {"title": "Devils on the Doorstep", "year": "1999"},
        {"title": "WALL-E", "year": "2008"},
        {"title": "The Pork of Music", "year": "2012"},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m["title"], year=m["year"])
        db.session.add(movie)

    db.session.commit()
    click.echo("Done.")


@app.shell_context_processor
def make_shell_context():
    # 将相关的模型添加到 shell 上下文
    return {"db": db}


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.route("/")
def index():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/home")
def hello():
    return "Hello"


@app.route("/user/<name>")
def user_page(name):
    return f"User: {escape(name)}"


@app.route("/test")
def test_url_for():
    print(url_for("hello"))
    print(url_for("user_page", name="staick"))
    print(url_for("user_page", name="greyli"))
    print(url_for("test_url_for"))
    print(url_for("test_url_for", num="2"))
    return "Test page"


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
