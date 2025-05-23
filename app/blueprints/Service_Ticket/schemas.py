from app.extensions import ma
from app.models import db, ServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    services = fields.Nested('app.blueprints.service_type.schemas.ServiceTypeSchema', many=True)
    
    class Meta:
        model = ServiceTicket
        sqla_session = db.session
        load_instance = True
        include_fk = True
        
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
