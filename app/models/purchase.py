from typing import Optional

from flask import current_app as app
from .product import Product
from .product_in_cart import ProductInCart
from sqlalchemy import text
from datetime import datetime


class Purchase:
    def __init__(
            self,
            id: int,
            time_purchased: datetime,
            is_fulfilled: bool,
            time_of_fulfillment: datetime,
            cart_id: int,
            user_id: int,
            final_unit_price: int,
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

    @staticmethod
    def get_by_cart(cart_id):
        rows = app.db.execute(
            '''
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
            ''',
            cart_id=cart_id)

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

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT product_in_cart_id, time_purchased, is_fulfilled, time_of_fulfillment, cart_id, user_id, final_unit_price
FROM Purchase
WHERE user_id = :user_id
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              user_id=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

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
