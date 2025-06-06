from app.extensions import ma
from app.models import db, Customer
from app.blueprints.cars.schemas import CarSchema

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    cars = ma.Nested(CarSchema, many=True)
    
    class Meta:
        model = Customer
        sqla_session = db.session
        load_instance = True
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(exclude=['name', 'address', 'phone'])