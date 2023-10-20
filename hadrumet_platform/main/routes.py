from flask import render_template, Blueprint

bp_main = Blueprint('main', __name__)


@bp_main.get("/")
def home():
    return render_template("home.html", title="Home")
