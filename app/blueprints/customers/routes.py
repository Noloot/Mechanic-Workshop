from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Customer
from . import customers_bp
from app.extensions import limiter, cache



@customers_bp.route("/", methods=['GET'])
@cache.cached(timeout=30)
def get_customers():
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit
    
    query = select(Customer).offset(offset).limit(limit)
    result = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(result)

@customers_bp.route("/<int:id>", methods=['GET'])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({"Error": "Customer not found"}),404
    
    return customer_schema.jsonify(result)

@customers_bp.route("/", methods=['POST'])
@limiter.limit("15 per day", override_defaults=True)
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    new_customer = customer_data
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({"Message": "New customer added successfully!",
                    "customer": customer_schema.dump(new_customer)}), 201
    
@customers_bp.route('/<int:id>', methods=['PUT'])
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
