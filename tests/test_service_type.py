import unittest
from app import create_app
from app.models import db, Employee, ServiceType, Customer, Car, ServiceTicket
from werkzeug.security import generate_password_hash
from app.utils.util import encode_token
from datetime import date

class TestServiceType(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.employee = Employee(
                name = "Admin User",
                email = "admin@email.com",
                password = generate_password_hash("adminpass"),
                address = "123 Main St",
                phone = "111-222-3333",
                role = "mechanic",
                salary = 95000
            )
            
            db.session.add(self.employee)
            db.session.commit()
            
            self.admin_token = encode_token(user_id=self.employee.id, role="mechanic")
            self.auth_header = {
                "Authorization": f"Bearer {self.admin_token}"
            }
            
    def test_add_service_type_success(self):
        payload = {
            "name": "Brake Inspection",
            "description": "Detailed check of braking system",
            "price": 89.99
        }
        
        response = self.client.post(
            "/service_types/",
            json = payload,
            headers = self.auth_header
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("service_type", data)
        self.assertEqual(data["service_type"]["name"], "Brake Inspection")
        self.assertEqual(data["service_type"]["price"], 89.99)
        
    def test_add_service_type_missing_fields(self):
        payload = {
            "description": "No name or price"
        }

        response = self.client.post(
            "/service_types/",
            json=payload,
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("name", str(data).lower())
        self.assertIn("price", str(data).lower())

    def test_get_service_types_paginated(self):
        with self.app.app_context():
            for i in range(5):
                st = ServiceType(
                    name=f"Service {i}",
                    description=f"Description {i}",
                    price=50 + i
                )
                db.session.add(st)
            db.session.commit()

        response = self.client.get("/service_types/?page=1&per_page=3")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["page"], 1)
        self.assertEqual(data["per_page"], 3)
        self.assertEqual(len(data["service_types"]), 3)
        self.assertIn("total_service_types", data)

    def test_update_service_type_success(self):
        with self.app.app_context():
            service = ServiceType(
                name="Oil Change",
                description="Quick oil replacement",
                price=29.99
            )
            db.session.add(service)
            db.session.commit()
            service_id = service.id

        update_payload = {
            "name": "Premium Oil Change",
            "description": "Full synthetic oil and filter",
            "price": 59.99
        }

        response = self.client.put(
            f"/service_types/{service_id}",
            json=update_payload,
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "Premium Oil Change")
        self.assertEqual(data["price"], 59.99)
        self.assertIn("description", data)

    def test_delete_service_type_success(self):
        with self.app.app_context():
            service = ServiceType(
                name="Tire Rotation",
                description="Front and rear tire swap",
                price=25.00
            )
            db.session.add(service)
            db.session.commit()
            service_id = service.id

        response = self.client.delete(
            f"/service_types/{service_id}",
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("deleted", data["message"].lower())

        with self.app.app_context():
            deleted = db.session.get(ServiceType, service_id)
            self.assertIsNone(deleted)

    def test_assign_service_type_to_ticket(self):
        with self.app.app_context():
            customer = Customer(
                name="Test Customer",
                email="customer@email.com",
                password=generate_password_hash("custpass"),
                address="456 Lane",
                phone="999-888-7777",
                role="customer"
            )
            db.session.add(customer)
            db.session.commit()

            car = Car(
                make="Toyota",
                model="Camry",
                model_year=2020,
                color="White",
                customer_id=customer.id
            )
            db.session.add(car)
            db.session.commit()

            ticket = ServiceTicket(
                VIN="1234567890",
                service_date=date(2025, 6, 1),
                customer_id=customer.id,
                car_id=car.id,
                car_issue="Check Engine Light",
                is_major_damage=False
            )
            db.session.add(ticket)
            db.session.commit()

            service_type = ServiceType(
                name="Diagnostic Test",
                description="Computerized scan",
                price=70.00
            )
            db.session.add(service_type)
            db.session.commit()

            response = self.client.put(
                f"/service_types/{service_type.id}/assign_service_type/{ticket.id}",
                headers=self.auth_header
            )

            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn("ticket", data)
            self.assertIn("services", data["ticket"])
            self.assertEqual(len(data["ticket"]["services"]), 1)
            self.assertEqual(data["ticket"]["services"][0]["id"], service_type.id)
            
    def test_remove_service_type_from_ticket(self):
        with self.app.app_context():
            customer = Customer(
                name="Test Customer",
                email="customer@email.com",
                password=generate_password_hash("custpass"),
                address="456 Lane",
                phone="999-888-7777",
                role="customer"
            )
            db.session.add(customer)
            db.session.commit()

            car = Car(
                make="Toyota",
                model="Camry",
                model_year=2020,
                color="White",
                customer_id=customer.id
            )
            db.session.add(car)
            db.session.commit()

            service_type = ServiceType(
                name="Alignment",
                description="Wheel alignment service",
                price=120.00
            )
            db.session.add(service_type)
            db.session.commit()

            ticket = ServiceTicket(
                VIN="1111111111",
                service_date=date(2025, 6, 1),
                customer_id=customer.id,
                car_id=car.id,
                car_issue="Steering Pulling",
                is_major_damage=False,
                services=[service_type]
            )
            db.session.add(ticket)
            db.session.commit()

            response = self.client.put(
                f"/service_types/{service_type.id}/remove_service_type/{ticket.id}",
                headers=self.auth_header
            )

            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn("message", data)
            self.assertIn("remove", data["message"].lower())

            updated_ticket = db.session.get(ServiceTicket, ticket.id)
            self.assertEqual(len(updated_ticket.services), 0)
