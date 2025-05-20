from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import car_schema, cars_schema
from app.models import db, Car
from . import cars_bp


@cars_bp.route('/', methods=['GET'])
def get_cars():
    cars = db.session.execute(select(Car)).scalars().all()
    return cars_schema.jsonify(cars)

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
def update_car(id):
    car = db.session.get(Car, id)
    if not car:
        return jsonify({'message': 'Car not found'}), 404
    try:
        car = car_schema.load(request.json, instance=car)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return car_schema.jsonify(car)

@cars_bp.route('/<int:id>', methods=['DELETE'])
def delete_car(id):
    car = db.session.get(Car, id)
    if not car:
        return jsonify({'message': 'Car not found'}), 404
    db.session.delete(car)
    db.session.commit()
    return jsonify({'message': f'Car {id} deleted successfully'})
    