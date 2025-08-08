######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for YourResourceModel Model

Test cases can be run with the following:
    nosetests
    coverage report -m
"""

import os
import logging
from decimal import Decimal
import unittest
from service.models import Product, DataValidationError, db
from tests.factories import ProductFactory

DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///../db/test.db")


######################################################################
#  Product Model Test Cases
######################################################################
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """These run once per Test Suite"""
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            name="iPhone",
            description="Smartphone from Apple",
            price=Decimal("999.99"),
            available=True,
            category="Electronics",
        )
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "iPhone")
        self.assertEqual(product.description, "Smartphone from Apple")
        self.assertEqual(product.price, Decimal("999.99"))
        self.assertTrue(product.available)
        self.assertEqual(product.category, "Electronics")

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        logging.debug(product)
        self.assertIsNotNone(product.id)
        # Change it and save it
        product.description = "Updated description"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "Updated description")
        # Fetch it back and make sure the id hasn't changed
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "Updated description")

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["description"], product.description)
        self.assertEqual(Decimal(data["price"]), product.price)
        self.assertEqual(data["available"], product.available)
        self.assertEqual(data["category"], product.category.name)  # <-- FIXED here

    def test_deserialize_a_product(self):
        """It should deserialize a Product"""
        data = ProductFactory().serialize()
        product = Product()
        product.deserialize(data)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(product.price, Decimal(data["price"]))
        self.assertEqual(product.available, data["available"])
        self.assertEqual(product.category.name, data["category"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing data"""
        data = {"name": "iPhone"}
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_bad_data(self):
        """It should not deserialize a Product with bad data"""
        data = "this is not a dictionary"
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)
