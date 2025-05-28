from app.extensions import ma
from app.models import db, ServiceTicket
from marshmallow import fields, EXCLUDE

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    services = fields.Nested('app.blueprints.service_type.schemas.ServiceTypeSchema', many=True, dump_only=True)
    
    class Meta:
        model = ServiceTicket
        sqla_session = db.session
        load_instance = True
        include_fk = True
        
class ServiceTicketCreateSchema(ServiceTicketSchema):
    class Meta(ServiceTicketSchema.Meta):
        unknown = EXCLUDE
        
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

service_ticket_create_schema = ServiceTicketCreateSchema()
