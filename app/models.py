from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class= Base)

mechanic_ticket = db.Table(
    'mechanic_ticket',
    Base.metadata,
    db.Column('employee_id', db.ForeignKey('employee.id'), primary_key=True),
    db.Column('service_ticket_id', db.ForeignKey('service_ticket.id'), primary_key=True)
)

ticket_service = db.Table(
    'ticket_service',
    Base.metadata,
    db.Column('service_ticket_id', db.ForeignKey('service_ticket.id'), primary_key=True),
    db.Column('service_type_id', db.ForeignKey('service_types.id'), primary_key=True)
)

class ServiceTicket(Base):
    __tablename__ = 'service_ticket'
    
    id: Mapped[int] = mapped_column(primary_key= True)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customer.id'), nullable=False)
    car_id: Mapped[int] = mapped_column(db.ForeignKey('car.id'), nullable=False)
    VIN: Mapped[str] = mapped_column(db.String(220), nullable= False)
    car_issue:  Mapped[str] = mapped_column(db.String(500), nullable= True)
    is_major_damage: Mapped[bool] = mapped_column(db.Boolean, default=False)
    
    employee: Mapped[List['Employee']] = db.relationship('Employee', secondary=mechanic_ticket, back_populates='tickets')
    car: Mapped['Car'] = db.relationship('Car', backref="owner", lazy=True)
    services: Mapped[List['ServiceType']] = db.relationship('ServiceType', secondary=ticket_service, back_populates='tickets')
    
class Customer(Base):
    __tablename__ = 'customer'
    
    id: Mapped[int] = mapped_column(primary_key= True)
    name: Mapped[str] = mapped_column(db.String(250), nullable=False)
    email: Mapped[str] = mapped_column(db.String(359), nullable=False, unique=True)
    phone: Mapped[int] = mapped_column(db.String(250), nullable=False)
    address: Mapped[str] = mapped_column(db.String(250), nullable=False)
    password: Mapped[str] = mapped_column(db.String(350), nullable=False)
    role: Mapped[str] = mapped_column(db.String(50), nullable=False)
    
    cars: Mapped[List['Car']] = db.relationship(back_populates='customer')
    
class Employee(Base):
    __tablename__ = 'employee'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(150), nullable=False)
    email: Mapped[str] = mapped_column(db.String(300), unique=True)
    address: Mapped[str] = mapped_column(db.String(300), nullable=False)
    phone: Mapped[int] = mapped_column(db.String(250), nullable=False)
    password: Mapped[str] = mapped_column(db.String(350), nullable=False)
    salary: Mapped[int] = mapped_column()
    role: Mapped[str] = mapped_column(db.String(50), nullable=False)
    
    tickets: Mapped[List['ServiceTicket']] = db.relationship('ServiceTicket', secondary=mechanic_ticket, back_populates='employee')
    
class Car(Base):
    __tablename__ = 'car'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    color: Mapped[str] = mapped_column(db.String(50))
    make: Mapped[str] = mapped_column(db.String(100), nullable=False)
    model: Mapped[str] = mapped_column(db.String(100), nullable=False)
    model_year: Mapped[int] = mapped_column()
    

    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customer.id"))
    customer: Mapped['Customer'] = db.relationship(back_populates='cars')
    
class ServiceType(Base):
    __tablename__ = 'service_types'
        
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(db.String(300), nullable=True)
    price: Mapped[float] = mapped_column(db.Float(), nullable=False)
    
    tickets: Mapped[List['ServiceTicket']] = db.relationship('ServiceTicket', secondary=ticket_service, back_populates='services')