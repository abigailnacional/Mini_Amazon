from flask import current_app as app
from .product import Product
from typing import Optional


class ProductInCart:

    def __init__(
            self,
            id: int,
            product: Product,
            cart_id: int,
            seller_id: int,
            quantity: int
    ):
        self.id = id
        self.product = product
        self.cart_id = cart_id
        self.quantity = quantity
        self.seller_id = seller_id

    @staticmethod
    def increase_quantity(product_in_cart_id: int):  # product_in_cart_id refers to the id in the ProductInCart table
        app.db.execute_with_no_return(
            """
            UPDATE ProductInCart
            SET quantity = quantity + 1
            WHERE id = :id
            """,
            # TODO add upper bound
            id=product_in_cart_id,
        )

    @staticmethod
    def decrease_quantity(product_in_cart_id: int):
        app.db.execute_with_no_return(
            """
            UPDATE ProductInCart
            SET quantity = quantity - 1
            WHERE id = :id
            AND quantity > 1
            """,
            id=product_in_cart_id
        )

    @staticmethod
    def remove_from_cart(product_in_cart_id: int):
        app.db.execute_with_no_return(
            """
            DELETE FROM ProductInCart
            WHERE id = :id
            """,
            id=product_in_cart_id
        )

