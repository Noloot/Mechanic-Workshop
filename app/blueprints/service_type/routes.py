from flask import request, jsonify
from app.models import db, ServiceType
from marshmallow import ValidationError
from .schemas import service_type_schema, service_types_schema
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

@serviceType_bp.route("/", methods=['GET'])
def get_service_types():
    service_types = db.session.execute(select(ServiceType)).scalars().all()
    print("DEBUG: Retrieved service types:", service_types)
    return jsonify(service_types_schema.dump(service_types)), 200


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