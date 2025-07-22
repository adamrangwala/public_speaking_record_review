from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_db
from .models import User
from .forms import LoginForm

auth = Blueprint('auth', __name__)
login_manager = LoginManager()

def init_auth(app):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        db = get_db()
        return db.query(User).get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = verify_user(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.index'))
        flash('Invalid email or password')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

def create_user(email, password):
    db = get_db()
    user = User(email=email)
    user.set_password(password)
    db.add(user)
    db.commit()
    return user

def verify_user(email, password):
    db = get_db()
    user = db.query(User).filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None