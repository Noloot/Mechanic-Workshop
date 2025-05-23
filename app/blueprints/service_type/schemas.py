from app.extensions import ma
from app.models import db, ServiceType

class ServiceTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceType
        sqla_session = db.session
        load_instance = True
        include_fk = True
        
service_type_schema = ServiceTypeSchema()
service_types_schema = ServiceTypeSchema(many=True)