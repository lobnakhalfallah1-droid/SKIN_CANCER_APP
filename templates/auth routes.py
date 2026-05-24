"""
auth_routes.py  –  À intégrer dans votre app Flask
===================================================
Dépendances :
    pip install flask flask-sqlalchemy werkzeug

Structure recommandée :
    app.py              ← initialise Flask, SQLAlchemy, importe ce fichier
    models.py           ← modèle User (ci-dessous)
    auth_routes.py      ← routes /login, /signup, /logout
    templates/
        login.html
        signup.html
"""

# ─── models.py ────────────────────────────────────────────────────────────────

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name    = db.Column(db.String(80),  nullable=False)
    last_name     = db.Column(db.String(80),  nullable=False)
    role          = db.Column(db.String(50),  nullable=False, default='autre')
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    is_active     = db.Column(db.Boolean,     default=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# ─── auth_routes.py ───────────────────────────────────────────────────────────

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)
# from models import db, User   ← décommentez quand vous importez ce fichier

auth_bp = Blueprint('auth', __name__)


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si déjà connecté, rediriger vers le dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard'))   # adaptez le nom de votre route

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Veuillez remplir tous les champs.", "danger")
            return render_template('login.html')

        # ── Vérification : l'utilisateur existe-t-il ? ──────────────────────
        user = User.query.filter_by(username=username).first()

        if user is None:
            # Username introuvable → rediriger vers signup avec un message
            flash(
                f"L'identifiant « {username} » n'existe pas. "
                "Créez votre compte ci-dessous.",
                "warning"
            )
            return redirect(url_for('auth.signup'))

        # ── Username trouvé : vérifier le mot de passe ──────────────────────
        if not user.check_password(password):
            flash("Mot de passe incorrect. Veuillez réessayer.", "danger")
            return render_template('login.html')

        if not user.is_active:
            flash("Ce compte a été désactivé. Contactez un administrateur.", "danger")
            return render_template('login.html')

        # ── Succès : créer la session ────────────────────────────────────────
        session['user_id']   = user.id
        session['username']  = user.username
        session['role']      = user.role
        return redirect(url_for('dashboard'))   # adaptez le nom de votre route

    return render_template('login.html')


# ── SIGNUP ────────────────────────────────────────────────────────────────────
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        first_name       = request.form.get('first_name', '').strip()
        last_name        = request.form.get('last_name',  '').strip()
        username         = request.form.get('username',   '').strip()
        email            = request.form.get('email',      '').strip().lower()
        role             = request.form.get('role',       'autre').strip()
        password         = request.form.get('password',   '')
        confirm_password = request.form.get('confirm_password', '')

        # ── Validations ──────────────────────────────────────────────────────
        errors = []

        if not all([first_name, last_name, username, email, password]):
            errors.append("Tous les champs obligatoires doivent être remplis.")

        if len(username) < 3:
            errors.append("L'identifiant doit contenir au moins 3 caractères.")

        if len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères.")

        if password != confirm_password:
            errors.append("Les mots de passe ne correspondent pas.")

        # Vérifier unicité username
        if User.query.filter_by(username=username).first():
            errors.append(f"L'identifiant « {username} » est déjà utilisé.")

        # Vérifier unicité email
        if User.query.filter_by(email=email).first():
            errors.append("Cette adresse e-mail est déjà associée à un compte.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('signup.html')

        # ── Créer l'utilisateur ───────────────────────────────────────────────
        new_user = User(
            username   = username,
            email      = email,
            first_name = first_name,
            last_name  = last_name,
            role       = role,
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


# ── LOGOUT ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "success")
    return redirect(url_for('auth.login'))


# ─── app.py (exemple minimal) ─────────────────────────────────────────────────
"""
from flask import Flask
from models import db
from auth_routes import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY']          = 'CHANGEZ-CE-SECRET'       # clé secrète forte
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skincancer.db'  # ou PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()   # crée les tables au démarrage

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    return f"Bienvenue {session['username']} !"

if __name__ == '__main__':
    app.run(debug=True)
"""