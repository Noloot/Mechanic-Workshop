from app import create_app
from app.models import db, ServiceType
from sqlalchemy import select

app = create_app('DevelopmentConfig')

with app.app_context():
    service_types = [
        {"name": "Oil Change", "price": 29.99},
        {"name": "Tire Rotation", "price": 49.99},
        {"name": "Brake Inspection", "price": 39.99}
    ]
    
    for st in service_types:
        exists = db.session.execute(select(ServiceType).where(ServiceType.name == st["name"])).scalar_one_or_none()
        if not exists:
            db.session.add(ServiceType(name=st["name"], price=st["price"]))
            
    db.session.commit()
    print("Service types seeded")