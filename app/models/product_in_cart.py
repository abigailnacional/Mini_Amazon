from flask import current_app as app
from .product import Product


class ProductInCart:

    def __init__(self, product: Product, cart_id: int, seller_id: int, quantity: int):
        self.product = product
        self.cart_id = cart_id
        self.quantity = quantity
        self.seller_id = seller_id

    @staticmethod
    def increase_quantity(cart_id, product_id, seller_id):
        app.db.execute_non_select_statement(
            """
            UPDATE ProductInCart
            SET quantity = quantity + 1
            WHERE product_id = :product_id
            AND cart_id = :cart_id
            AND seller_id = :seller_id
            """,
            product_id=product_id,
            cart_id=cart_id,
            seller_id=seller_id
        )

    @staticmethod
    def decrease_quantity(cart_id, product_id, seller_id):
        app.db.execute_non_select_statement(
            """
                UPDATE ProductInCart
                SET quantity = quantity - 1
                WHERE product_id = :product_id
                AND cart_id = :cart_id
                AND seller_id = :seller_id
                """,
                product_id=product_id,
                cart_id=cart_id,
                seller_id=seller_id
            )
