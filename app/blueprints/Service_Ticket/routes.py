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

@serviceTicket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    
    from app.models import Mechanic
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'message': 'Mechanic not found'}), 404
    
    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
        
    return jsonify({'message': f'Mechanic {mechanic_id} assign to ticket {ticket_id}.'})

@serviceTicket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    
    from app.models import Mechanic
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'message': 'Mechanic not found'}), 404
    
    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
        
    return jsonify({'message': f'Mechanic {mechanic_id} removed from ticket {ticket_id}'})

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
    return service_ticket_schema.jsonify(ticket), 200

@serviceTicket_bp.route('/<int:id>', methods=['DELETE'])
def delete_ticket(id):
    ticket = db.session.get(ServiceTicket, id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': f'Ticket {id} deleted successfully'})