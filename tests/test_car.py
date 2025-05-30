import unittest
from app import create_app
from app.models import db, Customer, Car
from werkzeug.security import generate_password_hash
from app.utils.util import encode_token

class TestCar(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.customer = Customer(
                name = "Test User",
                email = "testuser@email.com",
                password = generate_password_hash("password"),
                address = "123 Main St",
                phone = "222-333-4444",
                role = "customer"
            )
            
            db.session.add(self.customer)
            db.session.commit()
            
            self.customer_id = self.customer.id
            self.token = encode_token(user_id = self.customer_id, role = "customer")
            self.auth_header = {
                "Authorization": f"Bearer {self.token}"
            }
            
    def test_add_car_success(self):
        payload = {
            "make": "Honda",
            "model": "Civic",
            "model_year": 2020,
            "color": "Blue",
            "customer_id": self.customer_id
        }

        response = self.client.post(
            "/cars/",
            json=payload,
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("car", data)
        self.assertEqual(data["car"]["make"], "Honda")
        self.assertEqual(data["car"]["model"], "Civic")
        self.assertEqual(data["car"]["model_year"], 2020)
        self.assertEqual(data["car"]["color"], "Blue")
        self.assertEqual(data["car"]["customer_id"], self.customer_id)

    def test_add_car_missing_fields(self):
        payload = {
            "color": "Red",
            "model_year": 2021
        }

        response = self.client.post(
            "/cars/",
            json=payload,
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("make", data)
        self.assertIn("model", data)
        self.assertIn("customer_id", data)

    def test_get_cars_paginated(self):
        with self.app.app_context():
            for i in range(3):
                car = Car(
                    color="Black",
                    make=f"Make{i}",
                    model=f"Model{i}",
                    model_year=2020 + i,
                    customer_id=self.customer.id
                )
                db.session.add(car)
            db.session.commit()

        response = self.client.get("/cars/?page=1&per_page=2")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["per_page"], 2)
        self.assertIsInstance(data["cars"], list)
        self.assertLessEqual(len(data["cars"]), 2)

    def test_get_car_by_id(self):
        with self.app.app_context():
            car = Car(
                color="Blue",
                make="Honda",
                model="Civic",
                model_year=2021,
                customer_id=self.customer.id
            )
            db.session.add(car)
            db.session.commit()
            car_id = car.id

        response = self.client.get(f"/cars/{car_id}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["id"], car_id)
        self.assertEqual(data["make"], "Honda")
        self.assertEqual(data["model"], "Civic")

    def test_update_car_success(self):
        with self.app.app_context():
            car = Car(
                color="Gray",
                make="Toyota",
                model="Corolla",
                model_year=2018,
                customer_id=self.customer.id
            )
            db.session.add(car)
            db.session.commit()
            car_id = car.id

        update_payload = {
            "color": "Red",
            "model_year": 2019
        }

        response = self.client.put(
            f"/cars/{car_id}",
            json=update_payload,
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("car", data)
        self.assertEqual(data["car"]["color"], "Red")
        self.assertEqual(data["car"]["model_year"], 2019)

    def test_update_car_unauthorized(self):
        with self.app.app_context():
            other_customer = Customer(
                name="Other User",
                email="otheruser@email.com",
                password=generate_password_hash("otherpass"),
                address="456 Side St",
                phone="999-888-7777",
                role="customer"
            )
            db.session.add(other_customer)
            db.session.commit()

            other_car = Car(
                color="Green",
                make="Ford",
                model="Focus",
                model_year=2017,
                customer_id=other_customer.id
            )
            db.session.add(other_car)
            db.session.commit()
            other_car_id = other_car.id

        update_payload = {
            "color": "Black"
        }

        response = self.client.put(
            f"/cars/{other_car_id}",
            json=update_payload,
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("unauthorized", data["message"].lower())


    def test_delete_car_successfully(self):
        with self.app.app_context():
            car = Car(
                color="Silver",
                make="Mazda",
                model="CX-5",
                model_year=2019,
                customer_id=self.customer.id
            )
            db.session.add(car)
            db.session.commit()
            car_id = car.id

        response = self.client.delete(
            f"/cars/{car_id}",
            headers=self.auth_header
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("deleted", data["message"].lower())

        with self.app.app_context():
            deleted = db.session.get(Car, car_id)
            self.assertIsNone(deleted)

    def test_search_car_by_make(self):
        with self.app.app_context():
            car1 = Car(make="Nissan", model="Altima", model_year=2021, color="Gray", customer_id=self.customer.id)
            car2 = Car(make="Nissan", model="Sentra", model_year=2022, color="Black", customer_id=self.customer.id)
            car3 = Car(make="Ford", model="Fusion", model_year=2020, color="Blue", customer_id=self.customer.id)
            db.session.add_all([car1, car2, car3])
            db.session.commit()

        response = self.client.get("/cars/search?make=Nissan")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        for car in data:
            self.assertIn("Nissan", car["make"])
