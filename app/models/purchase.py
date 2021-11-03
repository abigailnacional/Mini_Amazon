from flask import current_app as app
from .cart import Cart



class Purchase:
    def __init__(
            self,
            id,
            time_purchased,
            is_fulfilled,
            time_of_fulfillment,
            cart_id,
            user_id
    ):
        self.id = id
        self.time_purchased = time_purchased
        self.is_fulfilled = is_fulfilled
        self.time_of_fulfillment = time_of_fulfillment
        self.cart_id = cart_id
        self.user_id = user_id

    @staticmethod
    def get(product_in_cart_id):
        rows = app.db.execute(
            '''
            SELECT product_in_cart_id, time_purchased, is_fulfilled, time_of_fulfillment, cart_id, user_id
            FROM Purchase
            WHERE product_in_cart_id = :product_in_cart_id
            ''',
            product_in_cart_id=product_in_cart_id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT product_in_cart_id, time_purchased, is_fulfilled, time_of_fulfillment, cart_id, user_id
FROM Purchase
WHERE user_id = :user_id
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              user_id=uid,
                              since=since)
        return [Purchase(*row) for row in rows]
