from flask import request, jsonify
from app.models import db, ServiceType, ServiceTicket
from marshmallow import ValidationError
from .schemas import service_type_schema, service_types_schema
from app.blueprints.Service_Ticket.schemas import service_ticket_schema
from sqlalchemy import select
from . import serviceType_bp
from app.utils.util import admin_required

@serviceType_bp.route("/", methods=['POST'])
@admin_required
def add_service_type():
    try:
        data = request.get_json()
        service_type = service_type_schema.load(data)
    except ValidationError as e:
        return jsonify({e.messages}), 400
    
    db.session.add(service_type)
    db.session.commit()
    
    return jsonify({'message': 'Service type added', 'service_type': service_type_schema.dump(service_type)}), 201

@serviceType_bp.route('/<int:service_type_id>/assign_service_type/<int:ticket_id>', methods=['PUT'])
@admin_required
def assign_service_type_to_ticket(service_type_id, ticket_id):
    
    service_type = db.session.get(ServiceType, service_type_id)
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not service_type:
        return jsonify({'message': 'Service type not found'}), 404
    if not ticket:
        return jsonify({'message': 'Service ticket not found'}), 404
    
    if service_type not in ticket.services:
        ticket.services.append(service_type)
        db.session.commit()
        
    return jsonify({'message': f'Service type {service_type_id} assigned to ticket {ticket_id}', 'ticket': service_ticket_schema.dump(ticket)})

@serviceType_bp.route('/<int:service_type_id>/remove_service_type/<int:ticket_id>', methods=['PUT'])
@admin_required
def remove_service_type_from_ticket(service_type_id, ticket_id):
    
    service_type = db.session.get(ServiceType, service_type_id)
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not service_type or not ticket:
        return jsonify({'message': 'Invalid ID(s)'}), 404
    
    if service_type in ticket.services:
        ticket.services.remove(service_type)
        db.session.commit()
        
    return jsonify({'message': f'Service type {service_type_id} remove from ticket {ticket_id}'})

@serviceType_bp.route("/", methods=['GET'])
def get_service_types():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        total = db.session.execute(select(ServiceType)).scalars().all()
        total_count = len(total)
        
        query = select(ServiceType).offset(offset).limit(per_page)
        service_types = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_service_types': total_count,
            'service_types': service_types_schema.dump(service_types)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching service types', 'error': str(e)}), 500

@serviceType_bp.route('/<int:id>', methods=['PUT'])
@admin_required
def update_service(id):
    service_type = db.session.get(ServiceType, id)
    if not service_type:
        return jsonify({'message': 'Service not found'}), 404
    
    try:
        service_type = service_type_schema.load(request.json, instance=service_type)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return service_type_schema.jsonify(service_type), 200

@serviceType_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_service_type(id):
    service_type = db.session.get(ServiceType, id)
    if not service_type:
        return jsonify({'message': 'service type not found'})
    
    db.session.delete(service_type)
    db.session.commit()
    
    return jsonify({'message': f'Service type {id} deleted successfully'})