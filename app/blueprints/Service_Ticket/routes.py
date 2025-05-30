from flask import request, jsonify
from app.models import db, ServiceTicket, ServiceType
from marshmallow import ValidationError
from .schemas import service_ticket_schema, service_tickets_schema, service_ticket_create_schema
from sqlalchemy import select
from . import serviceTicket_bp
from app.extensions import limiter, cache
from app.utils.util import admin_required

@serviceTicket_bp.route('/', methods=['POST'])
@limiter.limit("15 per hour")
@admin_required
def add_ticket():
    
    data = request.get_json()
    service_type_ids = data.pop("service_type_ids", [])
    
    try:
        ticket = service_ticket_create_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    if service_type_ids:
        service_types = db.session.query(ServiceType).filter(ServiceType.id.in_(service_type_ids)).all()
        found_ids = {s.id for s in service_types}
        requested_ids = set(service_type_ids)
        
        missing_ids = requested_ids - found_ids
        if missing_ids:
            return jsonify({
                'message': 'Invalid service_type_ids',
                'invalid_ids': list(missing_ids)
            }), 400
            
        ticket.services = service_types
        
    db.session.add(ticket)
    db.session.commit()
    
    if ticket.is_major_damage:
        
        print(f"Simulated sending ticket {ticket.id} to sister site")
        
        return jsonify({'message': 'Ticket created and sent to sister site', 'ticket': service_ticket_schema.dump(ticket)}), 201
    
    return jsonify({'message': 'Ticekt created', 'ticket': service_ticket_schema.dump(ticket)}), 201

@serviceTicket_bp.route('/', methods=['GET'])
def get_tickets():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        total = db.session.execute(select(ServiceTicket)).scalars().all()
        total_count = len(total)
        
        query = select(ServiceTicket).offset(offset).limit(per_page)
        tickets = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_tickets': total_count,
            'tickets': service_tickets_schema.dump(tickets)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching Tickets', 'error': str(e)}), 500

@serviceTicket_bp.route('/<int:id>', methods=['GET'])
def get_ticket(id):
    ticket = db.session.get(ServiceTicket, id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'})
    return service_ticket_schema.jsonify(ticket)


@serviceTicket_bp.route('/<int:ticket_id>/assign-mechanic/<int:employee_id>', methods=['PUT'])
@limiter.exempt
@admin_required
def assign_mechanic(ticket_id, employee_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    
    from app.models import Employee
    employee = db.session.get(Employee, employee_id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    
    if employee not in ticket.employee:
        ticket.employee.append(employee)
        db.session.commit()
        
    return jsonify({'message': f'Employee {employee_id} assign to ticket {ticket_id}.'})

@serviceTicket_bp.route('/<int:ticket_id>/remove-mechanic/<int:employee_id>', methods=['PUT'])
@limiter.exempt
@admin_required
def remove_mechanic(ticket_id, employee_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    
    from app.models import Employee
    employee = db.session.get(Employee, employee_id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    
    if employee in ticket.employee:
        ticket.employee.remove(employee)
        db.session.commit()
        
    return jsonify({'message': f'Employee {employee_id} removed from ticket {ticket_id}'})

@serviceTicket_bp.route('/<int:id>', methods=['PUT']) 
@limiter.exempt
@admin_required
def update_ticket(id):
    ticket = db.session.get(ServiceTicket, id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    
    data = request.get_json()
    service_type_ids = data.pop("service_ticket_ids", [])
    
    try:
        ticket = service_ticket_create_schema.load(request.json, instance=ticket)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    if service_type_ids:
        service_types = db.session.query(ServiceType).filter(ServiceType.id.in_(service_type_ids)).all()
        found_ids = {s.id for s in service_types}
        requested_ids = set(service_type_ids)
        missing_ids = requested_ids - found_ids
        if missing_ids:
            return jsonify({
                'message': 'Invalid service_type_ids',
                'invalid_ids': list(missing_ids)
            }), 400
            
        ticket.services = service_types
    
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200

@serviceTicket_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_ticket(id):
    ticket = db.session.get(ServiceTicket, id)
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': f'Ticket {id} deleted successfully'})