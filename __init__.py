from random import seed
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '\xd4\xdaJ\x97\x0f\x99\xe5X\x19\xaa\xe57'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mdclinicals@localhost/linh'

    db.init_app(app)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .app import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app