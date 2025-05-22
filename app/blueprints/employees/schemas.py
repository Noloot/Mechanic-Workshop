from app.models import db, Employee
from app.extensions import ma

class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        sqla_session = db.session
        load_instance = True
        
employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)
login_schema = EmployeeSchema(exclude=['name', 'address', 'phone', 'salary'])