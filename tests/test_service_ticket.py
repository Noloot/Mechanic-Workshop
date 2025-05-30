import unittest
from app import create_app
from app.models import db, Employee, Car, ServiceTicket, ServiceType, Customer
from werkzeug.security import generate_password_hash
from datetime import date
from app.utils.util import encode_token

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.employee = Employee(
                name = "John Smith",
                email = "john@example.com",
                password = generate_password_hash("123"),
                address = "123 Main St",
                phone = "111-222-3333",
                role = "mechanic",
                salary = 80000
            )
            
            db.session.add(self.employee)

            self.customer = Customer(
                name = "Test Customer",
                email = "customer@email.com",
                address = "123 Main St",
                phone = "111-222-3333",
                password = generate_password_hash("123456"),
                role = "customer"
            )
            
            db.session.add(self.customer)
            db.session.commit()
            
            self.car = Car(
                make = "Toyota",
                model = "Camry",
                model_year = 2022,
                color = "Gray",
                customer_id = self.customer.id
            )
            
            db.session.add(self.car)
            
            self.service_type = ServiceType(
                name = "Oil Change",
                description = "Routine oil and filter replacement",
                price = 59.99
            )
            
            db.session.add(self.service_type)
            
            db.session.commit()
            
            self.customer_id = self.customer.id
            self.car_id = self.car.id
            self.service_type_id = self.service_type.id
            self.employee_id = self.employee.id
            
            self.token = encode_token(user_id = self.employee_id, role = "mechanic")
            self.auth_header = {
                "Authorization": f"Bearer {self.token}"
            }
            
    def test_create_ticket(self):
        payload = {
            "service_date": str(date.today()),
            "customer_id": self.customer_id,
            "car_id": self.car_id,
            "VIN": "123",
            "car_issue": "Strange noise from engine",
            "is_major_damage": False,
            "service_type_ids": [self.service_type_id]
        }
        
        response = self.client.post(
            "/tickets/",
            json = payload,
            headers = self.auth_header
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertIn("ticket", data)
        self.assertEqual(data["ticket"]["customer_id"], self.customer_id)
        self.assertEqual(data["ticket"]["car_id"], self.car_id)
        self.assertEqual(data["ticket"]["VIN"], "123")
        self.assertEqual(len(data["ticket"]["services"]), 1)
        
    def test_create_ticket_with_invalid_service_type_id(self):
        payload = {
            "service_date": str(date.today()),
            "customer_id": self.customer_id,
            "car_id": self.car_id,
            "VIN": "234",
            "car_issue": "Test invalid service type",
            "is_major_damgae": False,
            "service_type_ids": [99999]
        }
        
        response = self.client.post(
            "/tickets/",
            json = payload,
            headers = self.auth_header
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("invalid_ids", data)
        self.assertIn(99999, data["invalid_ids"])
        
    def test_create_ticket_missing_required_fields(self):
        payload = {
            "car_id": self.car_id,
            "car_issue": "Incomplete payload",
            "is_major_damage": False,
            "service_types_ids": [self.service_type_id]
        }
        
        response = self.client.post(
            "/tickets/",
            json = payload,
            headers = self.auth_header
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertTrue(any(field in data for field in ["service_date", "customer_id", "VIN"]))

    def test_get_tickets_paginated(self):
        with self.app.app_context():
            for i in range(2):
                ticket = ServiceTicket(
                    service_date=date.today(),
                    customer_id=self.customer_id,
                    car_id=self.car_id,
                    VIN=f"VIN{i+1}ABC",
                    car_issue=f"Issue #{i+1}",
                    is_major_damage=False,
                    services=[self.service_type]
                )
                
                db.session.add(ticket)
            db.session.commit()
                
            response = self.client.get("/tickets/")
            self.assertEqual(response.status_code, 200)
                
            data = response.get_json()
            self.assertEqual(data["page"], 1)
            self.assertEqual(data['per_page'], 10)
            self.assertGreaterEqual(data["total_tickets"], 2)
            self.assertIsInstance(data["tickets"], list)
            self.assertGreaterEqual(len(data["tickets"]), 2)
            
    def test_get_ticket_by_id(self):
        with self.app.app_context():
            ticket = ServiceTicket(
                service_date=date.today(),
                customer_id=self.customer_id,
                car_id=self.car_id,
                VIN="GET123VIN",
                car_issue="Brake issues",
                is_major_damage=False,
                services=[self.service_type]
            )
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

        response = self.client.get(f"/tickets/{ticket_id}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["id"], ticket_id)
        self.assertEqual(data["VIN"], "GET123VIN")
        self.assertEqual(data["customer_id"], self.customer_id)

    def test_get_ticket_by_id_not_found(self):
        response = self.client.get("/tickets/99999")  
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Ticket not found")

    def test_update_ticket(self):
        with self.app.app_context():
            ticket = ServiceTicket(
                service_date=date.today(),
                customer_id=self.customer_id,
                car_id=self.car_id,
                VIN="OLDVIN123",
                car_issue="Original issue",
                is_major_damage=False,
                services=[self.service_type]
            )
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

        new_service_type = ServiceType(
            name="Brake Inspection",
            description="Full brake system check",
            price=99.99
        )
        with self.app.app_context():
            db.session.add(new_service_type)
            db.session.commit()
            new_service_type_id = new_service_type.id

        update_payload = {
            "service_date": str(date.today()),
            "customer_id": self.customer_id,
            "car_id": self.car_id,
            "VIN": "NEWVIN456",
            "car_issue": "Updated issue",
            "is_major_damage": True,
            "service_type_ids": [new_service_type_id]
        }

        response = self.client.put(
            f"/tickets/{ticket_id}",
            json=update_payload,
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["VIN"], "NEWVIN456")
        self.assertEqual(data["car_issue"], "Updated issue")
        self.assertTrue(data["is_major_damage"])
        self.assertEqual(len(data["services"]), 1)
        self.assertEqual(data["services"][0]["id"], new_service_type_id)

    def test_delete_ticket(self):
        with self.app.app_context():
            ticket = ServiceTicket(
                service_date = date.today(),
                customer_id = self.customer_id,
                car_id = self.car_id,
                VIN = "DELETE123",
                car_issue = "Test delete",
                is_major_damage = False,
                services = [self.service_type]
            )
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

        response = self.client.delete(f"/tickets/{ticket_id}", headers=self.auth_header)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("deleted", data["message"].lower())

        with self.app.app_context():
            deleted_ticket = db.session.get(ServiceTicket, ticket_id)
            self.assertIsNone(deleted_ticket)

    def test_assign_mechanic_to_ticket(self):
        with self.app.app_context():
            ticket = ServiceTicket(
                service_date=date.today(),
                customer_id=self.customer_id,
                car_id=self.car_id,
                VIN="ASSIGN123",
                car_issue="Needs diagnostics",
                is_major_damage=False,
                services=[self.service_type]
            )
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

        response = self.client.put(
            f"/tickets/{ticket_id}/assign-mechanic/{self.employee_id}",
            headers=self.auth_header
        )
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("assign", data["message"].lower())

        with self.app.app_context():
            updated_ticket = db.session.get(ServiceTicket, ticket_id)
            self.assertEqual(len(updated_ticket.employee), 1)
            self.assertEqual(updated_ticket.employee[0].id, self.employee_id)

    def test_remove_mechanic_from_ticket(self):
        with self.app.app_context():
            ticket = ServiceTicket(
                service_date=date.today(),
                customer_id=self.customer_id,
                car_id=self.car_id,
                VIN="REMOVE123",
                car_issue="Check engine light",
                is_major_damage=False,
                services=[self.service_type],
                employee=[self.employee]
            )
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

        response = self.client.put(
            f"/tickets/{ticket_id}/remove-mechanic/{self.employee_id}",
            headers=self.auth_header
        )
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("removed", data["message"].lower())

        with self.app.app_context():
            updated_ticket = db.session.get(ServiceTicket, ticket_id)
            self.assertEqual(len(updated_ticket.employee), 0)
