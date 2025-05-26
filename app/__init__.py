from flask import Flask
from app.extensions import ma, limiter, cache
from app.models import db
from app.blueprints.customers import customers_bp
from app.blueprints.employees import employee_bp
from app.blueprints.cars import cars_bp
from app.blueprints.Service_Ticket import serviceTicket_bp
from app.blueprints.service_type import serviceType_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic API"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object((f'config.{config_name}'))
    
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(employee_bp, url_prefix='/employees')
    app.register_blueprint(cars_bp, url_prefix='/cars')
    app.register_blueprint(serviceTicket_bp, url_prefix='/tickets')
    app.register_blueprint(serviceType_bp, url_prefix='/service_types')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return app