from .schemas import mechanic_schema, mechanics_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Mechanic
from . import mechanics_bp
from app.extensions import cache
from app.utils.util import encode_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash

@mechanics_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials.email
        password = credentials.password
    except KeyError:
        return jsonify({'message': 'Invalid payload, expecting email and password'}), 400
    
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalar_one_or_none()
    
    if mechanic and check_password_hash(mechanic.password, password):
        auth_token = encode_token(mechanic.id)
        
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=30)
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
    
    mechanic.password = generate_password_hash(mechanic.password)
    
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
@token_required
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({'message': 'Mechanic not found'}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'Mechanic {id} deleted successfully'})
