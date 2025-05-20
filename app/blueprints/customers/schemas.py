from app.extensions import ma
from app.models import db, Customer

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        sqla_session = db.session
        load_instance = True
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)