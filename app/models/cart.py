from flask import current_app as app
from .product import Product
from .purchase import Purchase
from .product_in_cart import ProductInCart
from .coupon import Coupon
from typing import List, Optional
from datetime import datetime

"""
This class represents a user's cart. Each user has one current cart and the rest of their carts are past orders
"""


class Cart:

    def __init__(
            self,
            id: int,
            user_id: int,
            is_current: bool,
            time_purchased: Optional[datetime] = None,
            is_fulfilled: Optional[bool] = None,
            coupon_applied: Optional[str] = None
    ):
        self.id = id
        self.user_id = user_id
        self.is_current = is_current
        self.time_purchased = time_purchased
        self.is_fulfilled = is_fulfilled
        self.coupon_applied = coupon_applied
        self.number_of_items = 0

    """
    Get a list of the products currently in a user's cart 
    """
    def get_products_in_cart(self, page_num: Optional[int]=None) -> Optional[List[ProductInCart]]:
        query_string = """
            SELECT id, product_id, seller_id, quantity
            FROM ProductInCart
            WHERE cart_id = :cart_id
            ORDER BY product_id
            """
        if page_num:
            query_string = """
            SELECT id, product_id, seller_id, quantity
            FROM ProductInCart
            WHERE cart_id = :cart_id
            ORDER BY product_id
            LIMIT 20
            OFFSET ((:page_num - 1) * 20)
            """

        rows = app.db.execute(
            query_string,
            cart_id=self.id,
            page_num=page_num
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
            self.number_of_items += product_in_cart_row[3]
        return products_in_cart

    """
    Get a list of the purchases in a user's cart. This method is only applicable if the cart has been purchased and 
    is not the user's current cart
    """
    def get_purchases(self, page_num: Optional[int]=None) -> Optional[List[Purchase]]:
        purchases = Purchase.get_by_cart(self.id, page_num)
        return purchases

    """
    Returns the current price of the cart based on the price at this moment of the products in the cart.
    Not meant to return the "final" price that was actually paid for a cart
    """
    def get_total_current_price(self, coupon: Optional[Coupon]) -> int:
        total_price = 0
        for product_in_cart in self.get_products_in_cart():
            total_price += product_in_cart.get_total_price_to_pay(coupon)
        return total_price

    """
    Changes a current cart to a purchased cart
    """
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

    """
    Checks if a specific product sold by a specific seller is currently in the cart
    """
    def is_product_by_seller_in_cart(self, product_id, seller_id):
        return bool(
            app.db.execute(
            """
            SELECT id
            FROM ProductInCart
            WHERE cart_id = :cart_id
            AND product_id = :product_id
            AND seller_id = :seller_id
            """,
            cart_id=self.id,
            product_id=product_id,
            seller_id=seller_id
        ))

    """
    Adds a coupon code that has been applied to the cart to the database 
    """
    def add_coupon(self, coupon_code):
        app.db.execute_with_no_return(
            """
            UPDATE Cart
            SET coupon_applied = :coupon_applied
            WHERE id = :cart_id
            """,
            cart_id=self.id,
            coupon_applied=coupon_code
        )
        self.coupon_applied = coupon_code

    """
    Removes this cart's coupon code if one exists
    """
    def remove_coupon(self):
        app.db.execute_with_no_return(
            """
            UPDATE Cart
            SET coupon_applied = NULL
            WHERE id = :cart_id
            """,
            cart_id=self.id,
        )
        self.coupon_applied = None


    """
    Returns a cart for the given id
    """
    @staticmethod
    def get_cart_by_id(cart_id: Optional[int]) -> "Cart":
        rows = app.db.execute(
            """
            SELECT id, user_id, is_current, time_purchased, is_fulfilled, coupon_applied
            FROM Cart
            WHERE id = :cart_id
            """,
            cart_id=cart_id
        )
        return Cart(*(rows[0])) if rows else None

    """
    Returns the user's current cart. If the user does not have a cart, a new one is created
    """
    @staticmethod
    def get_current_cart(user_id: int) -> "Cart":
        rows = app.db.execute(
            """
            SELECT id, user_id, is_current, time_purchased, is_fulfilled, coupon_applied
            FROM Cart
            WHERE user_id = :user_id
            AND is_current
            """,
            user_id=user_id
        )
        if not rows:  # no cart found for user
            print('no cart for user')
            cart_id = Cart.create_new_cart(user_id)
            coupon_applied = None
        else:
            cart_id = rows[0][0]
            coupon_applied = rows[0][5]

        current_cart = Cart(
            id=cart_id,
            user_id=user_id,
            is_current=True,
            coupon_applied=coupon_applied
        )

        coupon = Coupon.get(coupon_applied)
        if coupon and (coupon.expiration_date < datetime.now() or not current_cart.is_product_by_seller_in_cart(
                coupon.product_id, coupon.seller_id
        )):
            current_cart.remove_coupon()

        return current_cart

    """
    Creates a new cart for the given user
    """
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

    """
    Gets the id of the user's current cart
    """
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

    """
    Gets all purchased carts for a user
    """
    @staticmethod
    def get_purchased_carts(user_id: int, page_num: int) -> List[Optional['Cart']]:
        rows = app.db.execute(
            """
            SELECT id, user_id, is_current, time_purchased, is_fulfilled, coupon_applied
            FROM Cart
            WHERE user_id = :user_id
            AND NOT is_current
            ORDER BY time_purchased DESC, id DESC
            LIMIT 20
            OFFSET ((:page_num - 1) * 20)
            """,
            user_id=user_id,
            page_num=page_num
        )

        return [Cart(*row) for row in rows] if rows else []

    # #Gets the number of products in a cart
    # def get_num_of_items(self) -> Optional[int]:
    #     total_items = 0
    #     for product_in_cart in self.get_products_in_cart():
    #         total_items += product_in_cart.quantity
    #     self.number_of_items = self.get_num_of_items()
    #     return total_items

