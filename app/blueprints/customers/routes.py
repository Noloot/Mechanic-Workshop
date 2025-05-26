from .schemas import customer_schema, customers_schema, login_schema
from app.blueprints.cars.schemas import cars_schema, car_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Customer, Car
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash

@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials.email
        password = credentials.password
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalar_one_or_none()
    
    if customer and check_password_hash(customer.password, password):
        auth_token = encode_token(customer.id, customer.role)
        
        response = {
            "Status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@customers_bp.route("/", methods=['POST'])
@limiter.limit("15 per day", override_defaults=True)
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    customer_data.password = generate_password_hash(customer_data.password)
    
    new_customer = customer_data
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({"Message": "New customer added successfully!",
                    "customer": customer_schema.dump(new_customer)}), 201

@customers_bp.route("/<int:customer_id>/cars", methods=['POST'])
@token_required
def add_car_for_customer(customer_id):
    if request.user_id != customer_id:
        return jsonify({'message': 'Unauthorized to add car for this customer'}), 403
    
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    
    try:
        car_data = request.get_json()
        car = car_schema.load(car_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    car.customer_id = customer.id
    db.session.add(car)
    db.session.commit()
    
    return jsonify({'message': 'Car added successfully for customer', 'car': car_schema.dump(car)}), 201

@customers_bp.route("/<int:customer_id>/cars", methods=['GET'])
def get_customer_cars(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'})
    
    return cars_schema.jsonify(customer.cars), 200

@customers_bp.route("/", methods=['GET'])
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        offset = (page - 1) * per_page
        total = db.session.execute(select(Customer)).scalars().all()
        total_count = len(total)
            
        query = select(Customer).offset(offset).limit(per_page)
        customers = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_customers': total_count,
            "customers": customers_schema.dump(customers)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching Customers', 'error': str(e)}), 500

@customers_bp.route("/<int:id>", methods=['GET'])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({"Error": "Customer not found"}),404
    
    return customer_schema.jsonify(result)

@customers_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"message": "Invalid customer id"}), 404
    
    try:
        customer = customer_schema.load(request.json, instance=customer)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customers_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("3 per day")
def delete_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"message": "Invalid  customer id"}), 400
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"successfully deleted customer {id}"}), 200
