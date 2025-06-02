import unittest
from app import create_app
from app.models import db, Employee
from werkzeug.security import generate_password_hash

class TestEmployee(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        self.employee = Employee(
            name = "Jane Doe",
            email = "Jane@email.com",
            address = "101 Main St",
            phone = "111-222-3333",
            password = generate_password_hash("1234"),
            salary = 60000,
            role = "mechanic"
        )
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.employee)
            db.session.commit()
            self.employee_id = self.employee.id
            
    def test_create_employee(self):
        payload = {
            "name": "Marcquez Tookes",
            "email": "MTookes@email.com",
            "address": "123 Main St",
            "phone": "222-333-4444",
            "password": "12345",
            "salary": 100000,
            "role": "mechanic"
        }
        
        response = self.client.post('/employees/', json = payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("employee", response.json)
        self.assertEqual(response.json['employee']['email'], "MTookes@email.com")
        
    def test_create_employee_invalid(self):
        payload = {
            "name": "No Email",
            "address": "No Where",
            "phone": "000000000",
            "password": "pass",
            "salary": 0,
            "role": "mechanic"
        }
        
        response = self.client.post('/employees/', json = payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json)
        
    def test_employee_login(self):
        login_payload = {
            "email": "Jane@email.com",
            "password": "1234",
            "role": "mechanic"
        }
        
        response = self.client.post('/employees/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("auth_token", response.json)
        
    def test_employee_login_invalid(self):
        login_payload = {
            "email": "Jane@email.com",
            "password": "wrongpassword",
            "role": "mechanic"
        }
        
        response = self.client.post('/employees/login', json=login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], "Invalid email or password")
        
    def test_get_employees(self):
        response = self.client.get('/employees/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("employees", response.json)
        self.assertGreaterEqual(len(response.json["employees"]), 1)
        
    def test_get_employee_by_id(self):
        response = self.client.get(f'/employees/{self.employee_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], "Jane@email.com")
        
    def test_get_employee_by_invalid_id(self):
        response = self.client.get('/employees/2000')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Employee not found")
        
    def test_update_employee(self):
        from app.utils.util import encode_token
        token = encode_token(self.employee_id, "mechanic")
        headers = {'Authorization': f'Bearer {token}'}
        
        update_payload = {
            "name": "Jane Updated",
            "email": "Jane@email.com",
            "address": "202 Updated Blvd",
            "phone": "999-888-7777",
            "password": "4321",
            "salary": 80000,
            "role": "mechanic"
        }
        
        response = self.client.put(
            f'/employees/{self.employee_id}',
            json=update_payload,
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Jane Updated")
        self.assertEqual(response.json['address'], "202 Updated Blvd")
        self.assertEqual(response.json['phone'], "999-888-7777")
        
    def test_delete_employee(self):
        from app.utils.util import encode_token
        token = encode_token(self.employee_id, "mechanic")
        headers = {'Authorization': f'Bearer {token}'}
        
        response = self.client.delete(f'/employees/{self.employee_id}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], f"Employee {self.employee_id} deleted successfully")
        
        follow_up = self.client.get(f'/employees/{self.employee_id}')
        self.assertEqual(follow_up.status_code, 404)
        
    def test_get_employees_working_tickets(self):
        from app.models import ServiceTicket, Customer, Car
        from datetime import date
        
        with self.app.app_context():
            
            customer = Customer(
                name = "Test Customer",
                email = "testcustomer@email.com",
                address = "123 Main St",
                phone = "111-222-3333",
                password = generate_password_hash("password"),
                role = "customer"
            )
            db.session.add(customer)
            db.session.commit()
            
            car = Car(
                make = "Honda",
                model = "Civic",
                model_year = 2022,
                color = "Blue",
                customer_id = customer.id
            )
            db.session.add(car)
            db.session.commit()
            
            ticket = ServiceTicket(
                service_date = date.today(),
                customer_id = customer.id,
                car_id = car.id,
                VIN = "123",
                car_issue = "Engine overheating",
                is_major_damage = False
            )
            
            employee = db.session.get(Employee, self.employee_id)
            employee.tickets.append(ticket)
            
            db.session.add(ticket)
            db.session.commit()
            
        response = self.client.get('/employees/working_tickets')
        self.assertEqual(response.status_code, 200)
        
        data = response.json
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        
        mechanic = data[0]
        self.assertEqual(mechanic["id"], self.employee_id)
        self.assertEqual(mechanic["name"], self.employee.name)
        self.assertEqual(mechanic["ticket_count"], 1)
        self.assertIsInstance(mechanic["ticket_ids"], list)
        self.assertEqual(len(mechanic["ticket_ids"]), 1)