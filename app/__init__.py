import os
from flask import Flask, render_template  # ✅ render_template ici (pas en double)
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from flask_login import LoginManager  # ✅ Ajouté (tu utilises login_manager)
from .extensions import db, login_manager, migrate  # ✅ Import des extensions



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        database_url = 'sqlite:///../instance/bokoma.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # ✅ Optionnel mais recommandé
    migrate.init_app(app, db)

    # User loader pour Flask-Login
    from .models import User  # ✅ Import local pour éviter les boucles
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Admin
    from .models import Product  # ✅ Import local
    from .admin import MyAdminIndexView, MyModelView
    admin = Admin(
        app,
        name='BOKOMA-Admin',
        index_view=MyAdminIndexView()
    )
    admin.add_view(MyModelView(Product, db.session))
    admin.add_view(MyModelView(User, db.session))

    # Routes
    from .routes import main
    app.register_blueprint(main)

    # Gestion des erreurs
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('500.html'), 500

    # Création des tables (optionnel avec Flask-Migrate, mais utile en dev)
    with app.app_context():
        db.create_all()

    return app