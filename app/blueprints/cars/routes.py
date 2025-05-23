from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import car_schema, cars_schema
from app.models import db, Car
from . import cars_bp
from app.extensions import limiter
from app.utils.util import token_required

@cars_bp.route('/search', methods=['GET'])
def search_car():
    make = request.args.get('make')
    
    query = select(Car).where(Car.make.like(f'%{make}%'))
    cars = db.session.execute(query).scalars().all()
    
    return cars_schema.jsonify(cars)

@cars_bp.route('/', methods=['GET'])
def get_cars():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        offset = (page - 1) * per_page
        total = db.session.execute(select(Car)).scalars().all()
        total_count = len(total)
        
        query = select(Car).offset(offset).limit(per_page)
        cars = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'cars': cars_schema.dump(cars)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching Cars', 'error': str(e)}), 500

@cars_bp.route('/<int:id>', methods=['GET'])
def get_car(id):
    car = db.session.get(Car, id)
    if not car:
        return jsonify({'message': 'Car not found'}), 404
    return car_schema.jsonify(car)

@cars_bp.route('/', methods=['POST'])
def add_car():
    try: 
        car = car_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    db.session.add(car)
    db.session.commit()
    return jsonify({'message': 'Car added', 'car': car_schema.dump(car)}), 201

@cars_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_car(id):
    car = db.session.get(Car, id)
    if not car:
        return jsonify({'message': 'Car not found'}), 404
    
    if request.user_id != car.customer_id and request.user_role != 'mechanic':
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        updated_car = car_schema.load(request.json, instance=car, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return jsonify({'message': 'Car updated successfully', 'car': car_schema.dump(updated_car)}), 200

@cars_bp.route('/<int:id>', methods=['DELETE'])
def delete_car(id):
    car = db.session.get(Car, id)
    if not car:
        return jsonify({'message': 'Car not found'}), 404
    db.session.delete(car)
    db.session.commit()
    return jsonify({'message': f'Car {id} deleted successfully'})
    