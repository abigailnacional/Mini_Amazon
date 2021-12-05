from typing import Optional

from flask import current_app as app
from flask import render_template
from .product import Product
from .product_in_cart import ProductInCart
from sqlalchemy import text
from datetime import datetime

"""
This class represents a purchased product in a cart
"""


class Purchase:
    def __init__(
            self,
            id: int,
            time_purchased: datetime,
            is_fulfilled: bool,
            time_of_fulfillment: datetime,
            cart_id: int,
            user_id: int,
            final_unit_price: float,
            product_in_cart: Optional[ProductInCart] = None
    ):
        self.id = id
        self.time_purchased = time_purchased
        self.is_fulfilled = is_fulfilled
        self.time_of_fulfillment = time_of_fulfillment
        self.cart_id = cart_id
        self.user_id = user_id
        self.final_unit_price = final_unit_price
        self.product_in_cart = product_in_cart

    def get_total_price_paid(self, coupon):
        discount = 0
        if coupon and coupon.product_id == self.product_in_cart.product.id and \
                coupon.seller_id == self.product_in_cart.seller_id:
            discount = float(self.final_unit_price) * (coupon.percent_off / 100)
        return round((float(self.final_unit_price) * self.product_in_cart.quantity) - discount, 2)

    """
    Gets all the purchases for a certain cart with all relevant data, which also comes from ProductInCart
    """
    @staticmethod
    def get_by_cart(cart_id, page_num: Optional[int]=None):
        query_string = '''
            SELECT 
            Purchase.product_in_cart_id as product_in_cart_id, 
            Purchase.time_purchased as time_purchased, 
            Purchase.is_fulfilled as is_fulfilled, 
            Purchase.time_of_fulfillment as time_of_fulfillment, 
            Purchase.cart_id as cart_id, 
            Purchase.user_id as user_id,
            Purchase.final_unit_price as final_unit_price,
            ProductInCart.product_id as product_id,
            ProductInCart.seller_id as seller_id, 
            ProductInCart.quantity as quantity
            FROM Purchase
            JOIN ProductInCart
            ON ProductInCart.id=Purchase.product_in_cart_id
            WHERE Purchase.cart_id = :cart_id
            '''
        if page_num:
            query_string = '''
                SELECT 
                Purchase.product_in_cart_id as product_in_cart_id, 
                Purchase.time_purchased as time_purchased, 
                Purchase.is_fulfilled as is_fulfilled, 
                Purchase.time_of_fulfillment as time_of_fulfillment, 
                Purchase.cart_id as cart_id, 
                Purchase.user_id as user_id,
                Purchase.final_unit_price as final_unit_price,
                ProductInCart.product_id as product_id,
                ProductInCart.seller_id as seller_id, 
                ProductInCart.quantity as quantity
                FROM Purchase
                JOIN ProductInCart
                ON ProductInCart.id=Purchase.product_in_cart_id
                WHERE Purchase.cart_id = :cart_id
                LIMIT 20
                OFFSET ((:page_num - 1) * 20)
                '''
        rows = app.db.execute(
            query_string,
            cart_id=cart_id,
            page_num=page_num
        )

        return [
            Purchase(
                id=product_in_cart_id,
                time_purchased=time_purchased,
                is_fulfilled=is_fulfilled,
                time_of_fulfillment=time_of_fulfillment,
                cart_id=cart_id,
                user_id=user_id,
                final_unit_price=final_unit_price,
                product_in_cart=ProductInCart(
                    id=product_in_cart_id,
                    cart_id=cart_id,
                    seller_id=seller_id,
                    quantity=quantity,
                    product=Product.get(product_id)
            )) for (
                product_in_cart_id,
                time_purchased,
                is_fulfilled,
                time_of_fulfillment,
                cart_id,
                user_id,
                final_unit_price,
                product_id,
                seller_id,
                quantity,
            ) in rows] if rows else []

    """
    This method inserts a new row into the Purchase table without committing it to allow for rollbacks while 
    purchasing a cart
    """
    @staticmethod
    def insert_new_purchase_without_commit(conn, product_in_cart_id, user_id, cart_id, final_unit_price):
        conn.execute(text(
            """
            INSERT INTO Purchase(product_in_cart_id, user_id, cart_id, final_unit_price)
            VALUES (:product_in_cart_id, :user_id, :cart_id, :final_unit_price)
            """),
            {
                "product_in_cart_id": product_in_cart_id,
                "user_id": user_id,
                "cart_id": cart_id,
                "final_unit_price": final_unit_price
            }
        )

    @staticmethod
    def get_seller_incoming_orders(seller_id: int):
        rows = app.db.execute(
            # (buyer information including address, date order placed, total amount/number of items, and overall fulfillment status)
            """
            SELECT Users.first_name, Users.last_name, Users.address, Purchase.time_purchased, ProductInCart.quantity, Purchase.is_fulfilled, Purchase.product_in_cart_id, Purchase.cart_id
            FROM Purchase
            JOIN ProductInCart ON ProductInCart.id = Purchase.product_in_cart_id
            JOIN Users ON Users.id = Purchase.user_id
            WHERE is_fulfilled = false
              AND ProductInCart.seller_id = :seller_id
            ORDER BY Purchase.time_purchased DESC
            """,
            seller_id=seller_id
        )

        return [
            {
                'first_name': row[0],
                'last_name': row[1],
                'address': row[2],
                'timestamp': row[3],
                'quantity': row[4],
                'fulfilled': row[5],
                'product_in_cart_id': row[6],
                'cart_id': row[7]
            } for row in rows
        ]

    @staticmethod
    def get_seller_fulfilled_orders(seller_id: int):
        rows = app.db.execute(
            # (buyer information including address, date order placed, total amount/number of items, and overall fulfillment status)
            """
            SELECT Users.first_name, Users.last_name, Users.address, Purchase.time_purchased, ProductInCart.quantity, Purchase.is_fulfilled, Purchase.product_in_cart_id
            FROM Purchase
            JOIN ProductInCart ON ProductInCart.id = Purchase.product_in_cart_id
            JOIN Users ON Users.id = Purchase.user_id
            WHERE is_fulfilled = true
              AND ProductInCart.seller_id = :seller_id
            ORDER BY Purchase.time_purchased DESC
            """,
            seller_id=seller_id
        )

        return [
            {
                'first_name': row[0],
                'last_name': row[1],
                'address': row[2],
                'timestamp': row[3],
                'quantity': row[4],
                'fulfilled': row[5],
                'product_in_cart_id': row[6],
            } for row in rows
        ]

    """
    This method updates a purchase's fulfillment status which could change the cart fulfillment status as well
    """
    @staticmethod
    def mark_as_fulfilled(id, cart_id):
        app.db.execute_with_no_return(
            """
            UPDATE Purchase
            SET is_fulfilled = :is_fulfilled, time_of_fulfillment = :time_of_fulfillment
            WHERE product_in_cart_id = :product_in_cart_id
            """,
            product_in_cart_id=id,
            is_fulfilled=True,
            time_of_fulfillment=datetime.now()
        )

        unfulfilled_purchases_in_cart = app.db.execute(
            """
            SELECT product_in_cart_id 
            FROM Purchase
            WHERE cart_id = :cart_id
            AND is_fulfilled = :is_fulfilled
            """,
            cart_id=cart_id,
            is_fulfilled=False
        )
        if not unfulfilled_purchases_in_cart:
            app.db.execute_with_no_return(
                """
                UPDATE CART
                SET is_fulfilled = :is_fulfilled
                WHERE id = :cart_id
                """,
                cart_id=cart_id,
                is_fulfilled=True,
            )




