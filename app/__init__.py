from flask import Flask
from app.extensions import ma
from app.models import db
from app.blueprints.customers import customers_bp
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.cars import cars_bp
from app.blueprints.Service_Ticket import serviceTicket_bp

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object((f'config.{config_name}'))
    
    ma.init_app(app)
    db.init_app(app)
    
    
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(cars_bp, url_prefix='/cars')
    app.register_blueprint(serviceTicket_bp, url_prefix='/tickets')
    
    return app