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

    @staticmethod
    def add_to_cart(product_id: int, seller_id: int, cart_id):
        rows = app.db.execute(
            """
            SELECT id
            FROM ProductInCart
            WHERE cart_id = :cart_id
            AND seller_id = :seller_id
            AND product_id = :product_id
            """,
            cart_id =cart_id,
            seller_id=seller_id,
            product_id=product_id
        )
        if rows:  # product with same seller already exists in cart
            product_in_cart_id = rows[0][0]
            ProductInCart.increase_quantity(product_in_cart_id)
        else:  # product with this seller must be newly added to cart
            app.db.execute_with_no_return(
                """
                INSERT INTO ProductInCart(cart_id, product_id, seller_id, quantity)
                VALUES (:cart_id, :product_id, :seller_id, :quantity)
                """,
                cart_id=cart_id,
                product_id=product_id,
                seller_id=seller_id,
                quantity=1
            )

