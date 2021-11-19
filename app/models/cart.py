from flask import current_app as app, flash
from .product import Product
from .purchase import Purchase
from .product_in_cart import ProductInCart
from typing import List, Optional
from datetime import datetime
from sqlalchemy import text
from app.errors import NOT_ENOUGH_MONEY

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

    def get_purchases(self) -> Optional[List[Purchase]]:
        purchases = Purchase.get_by_cart(self.id)
        return purchases

    def get_total_current_price(self) -> int:
        total_price = 0
        for product_in_cart in self.get_products_in_cart():
            total_price += product_in_cart.product.price * product_in_cart.quantity
        return total_price

    def convert_cart_to_purchase(self):

        # for each item, check inventory and person money
        # if ever too low, rollback whole transaction
        # decrement inventory and person money
        # add seller money
        # create purchase
        # add final price to purchase

        # if all was successful, make cart past cart and create new cart

        with app.db.engine.begin() as conn:

            for product_in_cart in self.get_products_in_cart():  # TODO need to add final prices somehow

                product_price_by_unit = conn.execute(text(
                    """
                    SELECT price
                    FROM Product
                    WHERE id = :product_id
                    """),
                    {"product_id": product_in_cart.product.id}
                ).first()[0]

                total_product_price = product_in_cart.quantity

                user_balance = conn.execute(text(
                    """
                    SELECT balance
                    FROM Users
                    WHERE id = :user_id
                    """),
                    {"user_id": self.user_id},
                ).first()[0]
                user_has_enough_money = user_balance >= total_product_price

                if not user_has_enough_money:
                    flash(NOT_ENOUGH_MONEY)
                    conn.rollback()
                    return False
                else:
                    conn.execute(text(
                        """
                        UPDATE Users
                        SET balance = balance - :product_price
                        WHERE id = :user_id
                        """),
                        {
                            "product_price": total_product_price,
                            "user_id": self.user_id
                         },
                    )

                    conn.execute(text(
                        """
                        INSERT INTO Purchase(product_in_cart_id, user_id, cart_id, final_unit_price)
                        VALUES (:product_in_cart_id, :user_id, :cart_id, :final_unit_price)
                        """),
                        {
                            "product_in_cart_id": product_in_cart.id,
                            "user_id": self.user_id,
                            "cart_id": self.id,
                            "final_unit_price": product_price_by_unit
                        }
                    )
            print('transaction successful')
            conn.commit()
            self.mark_as_purchased()
            Cart.create_new_cart(self.user_id)
            return True

    def mark_as_purchased(self):
        app.db.execute_with_no_return(
            """
            UPDATE Cart
            SET is_current = False, time_purchased = :time_purchased
            WHERE id = :cart_id
            """,
            time_purchased=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            cart_id=self.id
        )

    @staticmethod
    def get_cart_by_id(cart_id: Optional[int]) -> "Cart":
        rows = app.db.execute(
            """
            SELECT id, user_id, is_current, time_purchased, is_fulfilled
            FROM Cart
            WHERE id = :cart_id
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
            ORDER BY id DESC
            """,
            user_id=user_id
        )

        return [Cart(*row) for row in rows] if rows else []
