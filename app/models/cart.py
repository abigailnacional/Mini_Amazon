from flask import current_app as app
from .product import Product
from .product_in_cart import ProductInCart
from typing import List, Optional
from datetime import datetime


class Cart:

    def __init__(
            self,
            id: int,
            user_id: int,
            is_current: bool,
            time_purchased: Optional[datetime] = None,
            is_fulfilled: Optional[bool] = None
    ):
        self.id = id
        self.user_id = user_id
        self.is_current = is_current
        self.time_purchased = time_purchased
        self.is_fulfilled = is_fulfilled

    def get_products_in_cart(self) -> Optional[List[ProductInCart]]:
        rows = app.db.execute(
            """
            SELECT id, product_id, seller_id, quantity
            FROM ProductInCart
            WHERE cart_id = :cart_id
            ORDER BY product_id
            """,
            cart_id=self.id
        )

        products_in_cart = []
        for product_in_cart_row in rows:
            products_in_cart.append(
                ProductInCart(
                    id=product_in_cart_row[0],
                    product=Product.get(product_in_cart_row[1]),
                    cart_id=self.id,
                    seller_id=product_in_cart_row[2],
                    quantity=product_in_cart_row[3]
                ))
        return products_in_cart

    def get_total_price_of_cart(self) -> int:
        total_price = 0
        for product_in_cart in self.get_products_in_cart():
            total_price += product_in_cart.product.price * product_in_cart.quantity
        return total_price

    def convert_cart_to_purchase(self):
        app.db.execute_with_no_return(
            """
            UPDATE Cart
            SET is_current = False, time_purchased = :time_purchased
            WHERE id = :cart_id
            """,
            cart_id=self.id,
            time_purchased=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        for product_in_cart in self.get_products_in_cart():
            app.db.execute_with_no_return(
                """
                EXECUTE insert_purchase(:product_id, :user_id, :cart_id)
                """,
                product_id=product_in_cart.id,
                user_id=self.user_id,
                cart_id=self.id
            )

        Cart.create_new_cart(self.user_id)

    @staticmethod
    def get_cart_by_id(cart_id: Optional[int]) -> "Cart":
        rows = app.db.execute(
            """
            SELECT id, user_id, is_current, time_purchased, is_fulfilled
            FROM Cart
            WHERE cart_id = :cart_id
            """,
            cart_id=cart_id
        )
        return Cart(*(rows[0])) if rows else None

    @staticmethod
    def get_current_cart(user_id: int) -> "Cart":
        rows = app.db.execute(
            """
            SELECT id, user_id, is_current, time_purchased, is_fulfilled
            FROM Cart
            WHERE user_id = :user_id
            AND is_current
            """,
            user_id=user_id
        )
        cart_id = rows[0][0]
        if not rows:  # no cart found for user
            print('no cart for user')
            cart_id = Cart.create_new_cart(user_id)
        return Cart(
            id=cart_id,
            user_id=user_id,
            is_current=True,
        )

    @staticmethod
    def create_new_cart(user_id: int) -> int:
        app.db.execute_with_no_return(
            """
            INSERT INTO Cart(user_id)
                VALUES (:user_id)
            """,
            user_id=user_id,
        )
        return app.db.execute(
            """
            SELECT id
            FROM Cart
            WHERE user_id = :user_id
            AND is_current
            """,
            user_id=user_id,
        )[0][0]

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
    def get_purchased_carts(user_id: int) -> List[Optional['Cart']]:
        rows = app.db.execute(
            """
            SELECT id, user_id, is_current, time_purchased, is_fulfilled
            FROM Cart
            WHERE user_id = :user_id
            AND NOT is_current
            """,
            user_id=user_id
        )

        return [Cart(*row) for row in rows] if rows else []
