from flask import current_app as app
from .product import Product
from .product_in_cart import ProductInCart
from typing import List, Optional


class Cart:

    def __init__(self, id: int, user_id: int, is_current: bool):
        self.id = id
        self.user_id = user_id
        self.is_current = is_current

    @staticmethod
    def get_products_in_cart(cart_id: int) -> Optional[List[ProductInCart]]:
        rows = app.db.execute(
            """
            SELECT product_id, seller_id, quantity
            FROM ProductInCart
            WHERE cart_id = :cart_id
            ORDER BY product_id
            """,
            cart_id=cart_id
        )
        products_in_cart = []
        for product_in_cart_row in rows:
            products_in_cart.append(
                ProductInCart(
                    Product.get(product_in_cart_row[0]),
                    cart_id,
                    product_in_cart_row[1],
                    product_in_cart_row[2]
                ))
        return products_in_cart

    @staticmethod
    def get_total_price_of_cart(products_in_cart: List[ProductInCart]) -> int:
        total_price = 0
        for product_in_cart in products_in_cart:
            total_price += product_in_cart.product.price * product_in_cart.quantity
        return total_price

    @staticmethod
    def get_id_of_current_cart(user_id: int) -> Optional[int]:
        rows = app.db.execute(
            """
            SELECT id
            FROM Cart
            WHERE user_id = :user_id
            AND is_current
            """,
            user_id=user_id
        )
        if not rows:  # no cart found for user
            print('no cart for user')
            return None
        return rows[0][0]

    @staticmethod
    def convert_cart_to_purchase(cart_id):
        app.db.execute_non_select_statement(
            """
                UPDATE Cart
                SET is_current = False
                WHERE cart_id = :cart_id
                """,
            cart_id=cart_id,
        )
        # TODO add purchase to table (need to refine database design for this)
        # app.db.execute(
        #     """
        #         INSERT INTO Purchase( VALUES
        #         ()
        #         """,
        #     cart_id=cart_id,
        # )