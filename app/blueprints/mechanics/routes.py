from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Mechanic
from . import mechanics_bp


@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    result = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(result)

@mechanics_bp.route('/<int:id>', methods=['GET'])
def get_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({'message': 'Mechanic not found'}), 404
    return mechanic_schema.jsonify(mechanic)

@mechanics_bp.route('/', methods=['POST'])
def add_mechanic():
    try:
        mechanic = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 404
    
    
    db.session.add(mechanic)
    db.session.commit()
    return jsonify({'message': 'Mechanic added', 'mechanic': mechanic_schema.dump(mechanic)}), 201

@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({'message': 'Mechanic not found'}), 404
    try:
        mechanic = mechanic_schema.load(request.json, instance=mechanic)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({'message': 'Mechanic not found'}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'Mechanic {id} deleted successfully'})
