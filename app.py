from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
from marshmallow import ValidationError
from flask_marshmallow import Marshmallow
from datetime import date
from typing import List

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Mateo0106(@localhost/mechanic'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class= Base)
db.init_app(app)
ma = Marshmallow(app)

class ServiceTicket(Base):
    __tablename__ = 'service_ticket'
    
    id: Mapped[int] = mapped_column(primary_key= True)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customer.id'))
    VIN: Mapped[str] = mapped_column(db.String(220), nullable= False)
    car_id:  Mapped[str] = mapped_column(db.String(500), nullable= True)
    
class Customer(Base):
    __tablename__ = 'customer'
    
    id: Mapped[int] = mapped_column(primary_key= True)
    name: Mapped[str] = mapped_column(db.String(250), nullable=False)
    email: Mapped[str] = mapped_column(db.String(359), nullable=False, unique=True)
    phone: Mapped[int] = mapped_column(db.String(250), nullable=False)
    address: Mapped[str] = mapped_column(db.String(250), nullable=False)
    
    cars: Mapped[List['Car']] = db.relationship(back_populates='customer')
    
class Mechanic(Base):
    __tablename__ = 'mechanic'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(150), nullable=False)
    email: Mapped[str] = mapped_column(db.String(300), unique=True)
    address: Mapped[str] = mapped_column(db.String(300), nullable=False)
    phone: Mapped[int] = mapped_column(db.String(250), nullable=False)
    password: Mapped[str] = mapped_column(db.String(350), nullable=False)
    salary: Mapped[int] = mapped_column()
    
class Car(Base):
    __tablename__ = 'car'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    color: Mapped[str] = mapped_column(db.String(50))
    make: Mapped[str] = mapped_column(db.String(100), nullable=False)
    model: Mapped[str] = mapped_column(db.String(100), nullable=False)
    model_year: Mapped[int] = mapped_column()
    

    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customer.id"))
    customer: Mapped['Customer'] = db.relationship(back_populates='cars')

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        sqla_session = db.session
        load_instance = True
        
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        sqla_session = db.session
        load_instance = True

class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car
        sqla_session = db.session
        load_instance = True
        
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        sqla_session = db.session
        load_instance = True
        include_fk = True

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

car_schema = CarSchema()
car_schema = CarSchema(many=True)

service_ticket_schema = ServiceTicketSchema()
service_ticket_schema = ServiceTicketSchema(many=True)

@app.route('/')
def home():
    return "Home"

# ? This is the customer section

@app.route("/customers", methods=['GET'])
def get_customers():
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit
    
    query = select(Customer).offset(offset).limit(limit)
    result = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(result)

@app.route("/customers/<int:id>", methods=['GET'])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({"Error": "Customer not found"}),404
    
    return customer_schema.jsonify(result)

@app.route("/customers", methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'], address=customer_data['address'])
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({"Message": "New customer added successfully!",
                    "customer": customer_schema.dump(new_customer)}), 201
    
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"message": "Invalid customer id"}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.address = customer_data['address']
    customer.phone = customer_data['phone']
    
    db.session.commit()
    return customer_schema.jsonify(customer), 200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"message": "Invalid  customer id"}), 400
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"successfully deleted customer {id}"}), 200

# ? This is the service ticket

with app.app_context():
    db.create_all()
    
# with app.app_context():
#     with db.engine.begin() as conn:
#         conn.execute(db.text("SET FOREIGN_KEY_CHECKS = 0;"))
#         conn.execute(db.text("DROP TABLE IF EXISTS service_tickets;"))
#         conn.execute(db.text("SET FOREIGN_KEY_CHECKS = 1;"))

app.run(debug=True)