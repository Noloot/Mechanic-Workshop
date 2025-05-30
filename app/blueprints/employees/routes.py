from .schemas import employee_schema, employees_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Employee
from . import employee_bp
from app.extensions import cache
from app.utils.util import encode_token, admin_required
from werkzeug.security import generate_password_hash, check_password_hash

@employee_bp.route('/', methods=['POST'])
def add_employee():
    try:
        employee = employee_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 404
    
    employee.password = generate_password_hash(employee.password)
    
    db.session.add(employee)
    db.session.commit()
    return jsonify({'message': 'Employee added', 'employee': employee_schema.dump(employee)}), 201

@employee_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials.email
        password = credentials.password
    except KeyError:
        return jsonify({'message': 'Invalid payload, expecting email and password'}), 400
    
    query = select(Employee).where(Employee.email == email)
    employee = db.session.execute(query).scalar_one_or_none()
    
    if employee and check_password_hash(employee.password, password):
        auth_token = encode_token(employee.id, employee.role)
        
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401
    
@employee_bp.route('/working_tickets', methods=['GET'])
def tickets_working_on():
    query = select(Employee)
    mechanics = db.session.execute(query).scalars().all()
    
    mechanics.sort(key= lambda m: len(m.tickets), reverse=True)
    
    mechanics = [m for m in mechanics if m.tickets]
    
    result = [
        {
            "id": m.id,
            "name": m.name,
            "ticket_count": len(m.tickets),
            "ticket_ids": [t.id for t in m.tickets]
        }
        for m in mechanics
    ]
    
    return jsonify(result)

@employee_bp.route('/', methods=['GET'])
def get_employees():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page -1) * per_page
        total = db.session.execute(select(Employee)).scalars().all()
        total_count = len(total)
        
        query = select(Employee).offset(offset).limit(per_page)
        employees = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_employee': total_count,
            'employees': employees_schema.dump(employees)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching Employees', 'error': str(e)}), 500
        
@employee_bp.route('/<int:id>', methods=['GET'])
def get_employee(id):
    employee = db.session.get(Employee, id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    return employee_schema.jsonify(employee)


@employee_bp.route('/<int:id>', methods=['PUT'])
@admin_required
def update_employee(id):
    employee = db.session.get(Employee, id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    try:
        employee = employee_schema.load(request.json, instance=employee)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return employee_schema.jsonify(employee), 200

@employee_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_employee(id):
    employee = db.session.get(Employee, id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': f'Employee {id} deleted successfully'})
