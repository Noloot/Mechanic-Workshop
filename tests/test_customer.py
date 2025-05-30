from app import create_app
from app.models import db, Customer
import unittest
from app.utils.util import encode_token
from werkzeug.security import generate_password_hash

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name="John Doe", email="dj@email.com", address="123 Main St", password=generate_password_hash("123"), role="customer", phone="111-222-3333")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
            self.customer_id = self.customer.id
        self.token = encode_token(1, "customer")
        self.client = self.app.test_client()
        
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "address": "123 Main St",
            "password": "123",
            "role": "customer",
            "phone": "111-222-3333"
        }
        
        response = self.client.post('/customers/',json=customer_payload)
        self.assertEqual(response.status_code,201)
        print("DEBUG Response JSON:", response.json)
        self.assertEqual(response.json['customer']['name'],"John Doe")
        
    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "111-222-3333",
            "password": "123"
        }
        
        response = self.client.post('/customers/',json=customer_payload)
        self.assertEqual(response.status_code,400)
        self.assertEqual(response.json['email'],['Missing data for required field.'])
        
    def login_member(self):
        credentials = {
            "email": "dj@email.com",
            "password": "123",
            "role": "customer"
        }
        
        response = self.client.post('customers/login',json=credentials)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['Status'],'success')
        return response.json['auth_token']
    
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw",
            "role": "customer"
        }
        
        response = self.client.post('/customers/login',json=credentials)
        self.assertEqual(response.status_code,401)
        self.assertEqual(response.json['message'],'Invalid email or password')
        
    def test_update_customer(self):
        update_payload = {
            "name": "Peter",
            "phone": "",
            "email": "dj@email.com",
            "password": "",
            "address": "",
            "role": ""
        }
        
        headers = {'Authorization': "Bearer " + self.login_member()}
        
        response = self.client.put('customers/1',json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter')
        self.assertEqual(response.json['email'], 'dj@email.com')
        
    def test_get_all_customers(self):
        token = self.login_member()
        headers = {'Authorization': f'Bearer {token}'}
        
        response = self.client.get('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)
        customers = response.json.get('customers')
        self.assertIsInstance(customers, list)
        self.assertGreaterEqual(len(customers), 1)
        
    def test_get_customer_by_id(self):
        token = self.login_member()
        headers = {'Authorization': f'Bearer {token}'}
        
        response = self.client.get(f'/customers/{self.customer_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], self.customer.email)
        
    def test_delete_customer_by_id(self):
        token = self.login_member()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete(f'/customers/{self.customer_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
    
    def test_post_car_for_customer(self):
        token = self.login_member()
        headers = {'Authorization': f'Bearer {token}'}
        
        car_payload = {
            "make": "Toyota",
            "model": "Camry",
            "model_year": 2022,
            "color": "Black",
            "customer_id": 1
        }
        
        response = self.client.post(
            f'/customers/{self.customer_id}/cars',
            json=car_payload,
            headers=headers
        )
        
        print("DEBUG Car POST Response:", response.json)
        
        car_data = response.json['car']
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(car_data['make'], "Toyota")
        self.assertEqual(car_data['model'], "Camry")
        self.assertEqual(car_data['model_year'], 2022)
        self.assertEqual(car_data['color'], "Black")
        self.assertEqual(car_data['customer_id'], self.customer_id)
        
    def test_get_cars_for_customer(self):
        from app.models import Car
        
        with self.app.app_context():
            db.session.add(Car(
                make="Honda",
                model="Civic",
                model_year=2020,
                color="Red",
                customer_id=self.customer_id
            ))
            db.session.commit()
            
        response = self.client.get(f'/customers/{self.customer_id}/cars')
        self.assertEqual(response.status_code, 200)
        cars = response.json
        self.assertIsInstance(cars, list)
        self.assertGreaterEqual(len(cars), 1)
        car = cars[0]
        self.assertEqual(car['make'], "Honda")
        self.assertEqual(car['model'], "Civic")
        self.assertEqual(car['model_year'], 2020)
        self.assertEqual(car['color'], "Red")
        self.assertEqual(car['customer_id'], self.customer_id)