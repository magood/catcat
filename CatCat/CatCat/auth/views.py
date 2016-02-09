from flask import render_template, current_app, request, flash, redirect, session, url_for, request, g, make_response
from flask_login import login_user, logout_user, current_user, login_required
from CatCat import lm, db
from CatCat.models import User
from . import auth
from CatCat import authomatic
from authomatic.adapters import WerkzeugAdapter
from CatCat.FlaskAuthomatic import FlaskAuthomatic as fa
from authomatic.exceptions import ConfigError

@auth.route('/login')
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('auth/login.html',
                           title='Sign in')

@auth.route('/dologin/<providername>', methods=['GET', 'POST'])
def dologin(providername):
    #http://peterhudec.github.io/authomatic/examples/flask-simple.html
    response = make_response()
    # Authenticate the user
    #TODO which adapter to use depends on environment
    wa = fa.ForceHTTPSWerkzeugAdapter(request, response)
    if current_app.config['DEBUG'] == True:
        wa = WerkzeugAdapter(request, response)
    #Flask/nginx/gunicorn/whatever doesn't think its in a secure environment if its set up as a proxy pass, which currently it is in prod.
    #really wish i could get the server to realize its secure.
    try:
        result = authomatic.login(wa, providername)
    except (ConfigError):
        return redirect(url_for('main.home'))

    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # We need to update the user to get more info. (from oath provider?)
            result.user.update()
            #I think this is where we need to store the user in our system.
            user_email = result.user.email
            if user_email is None or user_email == "":
                flash('No email returned from OAuth provider. Please try another provider.')
                return redirect(url_for('auth.login'))
            user = User.query.filter_by(email=user_email).first()
            if user is None:
                #New user - add to system
                user = User(email=user_email, username=user_email, display_name=result.user.name)
                db.session.add(user)
                #todo handle duplicate email/usernames here.
                db.session.commit()
            #remember me won't work unless i re-implement the form login...
            remember_me = False
            if 'remember_me' in session:
                remember_me = session['remember_me']
                session.pop('remember_me', None)
            login_user(user, remember = remember_me)
            return redirect(request.args.get('next') or url_for('main.home'))

        #Matthew Good
        #matthewcgood@gmail.com
        #101662698174138733448
    #if no result, authomatic wants you to return the response...
    return response

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.before_app_request
def before_request():
    g.user = current_user