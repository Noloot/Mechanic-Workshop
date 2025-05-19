from app import create_app
from app.models import db


app = create_app('DevelopmentConfig')



# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# from sqlalchemy import select
# from marshmallow import ValidationError

# from datetime import date
# from typing import List

# app = Flask(__name__)

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False






        
# class MechanicSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Mechanic
#         sqla_session = db.session
#         load_instance = True

# class CarSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Car
#         sqla_session = db.session
#         load_instance = True
#         include_fk = True
        
# class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = ServiceTicket
#         sqla_session = db.session
#         load_instance = True
#         include_fk = True



# mechanic_schema = MechanicSchema()
# mechanics_schema = MechanicSchema(many=True)

# car_schema = CarSchema()
# cars_schema = CarSchema(many=True)

# service_ticket_schema = ServiceTicketSchema()
# service_tickets_schema = ServiceTicketSchema(many=True)

# @app.route('/')
# def home():
#     return "Home"

# # ? This is the Customer methods


# # ? This is the Mechanics method

# @app.route('/mechanics', methods=['GET'])
# def get_mechanics():
#     query = select(Mechanic)
#     result = db.session.execute(query).scalars().all()
#     return mechanics_schema.jsonify(result)

# @app.route('/mechanics/<int:id>', methods=['GET'])
# def get_mechanic(id):
#     mechanic = db.session.get(Mechanic, id)
#     if not mechanic:
#         return jsonify({'message': 'Mechanic not found'}), 404
#     return mechanic_schema.jsonify(mechanic)

# @app.route('/mechanics', methods=['POST'])
# def add_mechanic():
#     try:
#         mechanic = mechanic_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 404
    
    
#     db.session.add(mechanic)
#     db.session.commit()
#     return jsonify({'message': 'Mechanic added', 'mechanic': mechanic_schema.dump(mechanic)}), 201

# @app.route('/mechanics/<int:id>', methods=['PUT'])
# def update_mechanic(id):
#     mechanic = db.session.get(Mechanic, id)
#     if not mechanic:
#         return jsonify({'message': 'Mechanic not found'}), 404
#     try:
#         mechanic = mechanic_schema.load(request.json, instance=mechanic)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
    
#     db.session.commit()
#     return mechanic_schema.jsonify(mechanic), 200

# @app.route('/mechanics/<int:id>', methods=['DELETE'])
# def delete_mechanic(id):
#     mechanic = db.session.get(Mechanic, id)
#     if not mechanic:
#         return jsonify({'message': 'Mechanic not found'}), 404
    
#     db.session.delete(mechanic)
#     db.session.commit()
#     return jsonify({'message': f'Mechanic {id} deleted successfully'})

# # ? This is the Cars Methods

# @app.route('/cars', methods=['GET'])
# def get_cars():
#     cars = db.session.execute(select(Car)).scalars().all()
#     return cars_schema.jsonify(cars)

# @app.route('/cars/<int:id>', methods=['GET'])
# def get_car(id):
#     car = db.session.get(Car, id)
#     if not car:
#         return jsonify({'message': 'Car not found'}), 404
#     return car_schema.jsonify(car)

# @app.route('/cars', methods=['POST'])
# def add_car():
#     try: 
#         car = car_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
#     db.session.add(car)
#     db.session.commit()
#     return jsonify({'message': 'Car added', 'car': car_schema.dump(car)}), 201

# @app.route('/cars/<int:id>', methods=['PUT'])
# def update_car(id):
#     car = db.session.get(Car, id)
#     if not car:
#         return jsonify({'message': 'Car not found'}), 404
#     try:
#         car = car_schema.load(request.json, instance=car)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
    
#     db.session.commit()
#     return car_schema.jsonify(car)

# @app.route('/cars/<int:id>', methods=['DELETE'])
# def delete_car(id):
#     car = db.session.get(Car, id)
#     if not car:
#         return jsonify({'message': 'Car not found'}), 404
#     db.session.delete(car)
#     db.session.commit()
#     return jsonify({'message': f'Car {id} deleted successfully'})
    
# # ? This is the Tickets method

# @app.route('/tickets', methods=['GET'])
# def get_tickets():
#     tickets = db.session.execute(select(ServiceTicket)).scalars().all()
#     return service_tickets_schema.jsonify(tickets)

# @app.route('/tickets/<int:id>', methods=['GET'])
# def get_ticket(id):
#     ticket = db.session.get(ServiceTicket, id)
#     if not ticket:
#         return jsonify({'message': 'Ticket not found'})
#     return service_ticket_schema.jsonify(ticket)

# @app.route('/tickets', methods=['POST'])
# def add_ticket():
#     try:
#         ticket = service_ticket_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
    
    
#     db.session.add(ticket)
#     db.session.commit()
#     return jsonify({'message': 'Ticekt created', 'ticket': service_ticket_schema.dump(ticket)}), 201

# @app.route('/tickets/<int:id>', methods=['PUT'])
# def update_ticket(id):
#     ticket = db.session.get(ServiceTicket, id)
#     if not ticket:
#         return jsonify({'message': 'Ticket not found'}), 404
#     try:
#         ticket = service_ticket_schema.load(request.json, instance=ticket)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
    
#     db.session.commit()
#     return service_ticket_schema.jsonify(ticket)

# @app.route('/tickets/<int:id>', methods=['DELETE'])
# def delete_ticket(id):
#     ticket = db.session.get(ServiceTicket, id)
#     if not ticket:
#         return jsonify({'message': 'Ticket not found'}), 404
#     db.session.delete(ticket)
#     db.session.commit()
#     return jsonify({'message': f'Ticket {id} deleted successfully'})

with app.app_context():
    # db.drop_all()
    db.create_all()
    

app.run()