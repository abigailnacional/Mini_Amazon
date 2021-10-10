from flask import current_app as app
from .product import Product


class ProductInCart:

    def __init__(self, product: Product, cart_id: int, quantity: int):
        self.product = product
        self.cart_id = cart_id
        self.quantity = quantity

    @staticmethod
    def increase_quantity(cart_id, product_id):
        app.db.execute_non_select_statement(
            """
            UPDATE ProductsInCart
            SET quantity = quantity + 1
            WHERE product_id = :product_id
            AND cart_id = :cart_id
            """,
            product_id=product_id,
            cart_id=cart_id
        )

    @staticmethod
    def decrease_quantity(cart_id, product_id):
        app.db.execute_non_select_statement(
            """
                UPDATE ProductsInCart
                SET quantity = quantity - 1
                WHERE product_id = :product_id
                AND cart_id = :cart_id
                """,
                product_id=product_id,
                cart_id=cart_id
            )
