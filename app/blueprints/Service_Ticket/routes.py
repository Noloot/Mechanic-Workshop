from flask import request, jsonify
from app.models import db, ServiceTicket
from marshmallow import ValidationError
from .schemas import service_ticket_schema, service_tickets_schema
from sqlalchemy import select
from . import serviceTicket_bp


@serviceTicket_bp.route('/', methods=['GET'])
def get_tickets():
    tickets = db.session.execute(select(ServiceTicket)).scalars().all()
    return service_tickets_schema.jsonify(tickets)

@serviceTicket_bp.route('/<int:id>', methods=['GET'])
def get_ticket(id):
    ticket = db.session.get(ServiceTicket, id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'})
    return service_ticket_schema.jsonify(ticket)

@serviceTicket_bp.route('/', methods=['POST'])
def add_ticket():
    try:
        ticket = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    
    db.session.add(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticekt created', 'ticket': service_ticket_schema.dump(ticket)}), 201

@serviceTicket_bp.route('/<int:id>', methods=['PUT'])
def update_ticket(id):
    ticket = db.session.get(ServiceTicket, id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    try:
        ticket = service_ticket_schema.load(request.json, instance=ticket)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return service_ticket_schema.jsonify(ticket)

@serviceTicket_bp.route('/<int:id>', methods=['DELETE'])
def delete_ticket(id):
    ticket = db.session.get(ServiceTicket, id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': f'Ticket {id} deleted successfully'})