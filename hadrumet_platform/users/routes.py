from flask import render_template, Blueprint, request, redirect, url_for, session, flash
from hadrumet_platform import oauth, get_database
from authlib.common.security import generate_token

db = get_database()
db_member = db.member

bp_users = Blueprint('users', __name__)

@bp_users.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        member = db_member.find_one({"email": email})
        print(member)

        if member:
            if member["date_leaving"] == "":
                allow_form_login = member["allow_form_login"]
                if allow_form_login:
                    if member["password"] == password:
                        return redirect(url_for("main.home"))
                    else:
                        flash("Email or password incorrect.", "danger")
                        return redirect(url_for("users.login"))
                else:
                    flash("You are unable to login using your personal email.", "warning")
                    return redirect(url_for("users.login"))
        else:
            flash("An error has occured.", "warning")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login")

@bp_users.route("/google")
def google():
    GOOGLE_CLIENT_ID = ''
    GOOGLE_CLIENT_SECRET = ''

    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # Redirect to google_auth function
    redirect_uri = url_for('users.google_auth', _external=True)
    session['nonce'] = generate_token()
    return oauth.google.authorize_redirect(redirect_uri)

@bp_users.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token, None)

    member = db_member.find_one({"email": user["email"]})
    if member:
        if member["date_leaving"] == "":
            session['user'] = user
            return redirect(url_for("main.home"))
        else:
            flash("An error has occured.", "warning")
            return redirect(url_for("users.login"))

    print(" Google User ", user)

    return redirect(url_for("main.home"))