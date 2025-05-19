from flask import Flask
from app.extensions import ma
from app.models import db
from app.blueprints.customers import customers_bp
from app.blueprints.mechanics import mechanics_bp

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object((f'config.{config_name}'))
    
    ma.init_app(app)
    db.init_app(app)
    
    
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    
    return app