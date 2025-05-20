from app.extensions import ma
from app.models import db, Car


class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car
        sqla_session = db.session
        load_instance = True
        include_fk = True
        
car_schema = CarSchema()
cars_schema = CarSchema(many=True)