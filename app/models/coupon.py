from datetime import datetime
from flask import current_app as app
import string
import random
import datetime
from .product import Product
from .user import User

letters = string.ascii_lowercase
PERCENT_OFF = 50  # currently a constant half off, but could change in the future

"""
This class represents a coupon that a user may use to get some percent off a specific product from a specific seller
prior to the coupon's expiration date
"""


class Coupon:

    def __init__(
            self,
            code: str,
            expiration_date: datetime,
            product_id: int,
            seller_id: int,
            percent_off: float,
    ):
        self.code = code
        self.expiration_date = expiration_date
        self.product_id = product_id
        self.seller_id = seller_id
        self.percent_off = percent_off

        self.product_name = self.get_product_name()
        self.seller_name = self.get_seller_name()

    """
    Checks if the coupon has expired
    """
    def is_expired(self):
        return datetime.datetime.now() <= self.expiration_date

    """
    Returns the name of the product for which the coupon applies
    """
    def get_product_name(self):
        return Product.get(self.product_id).name

    """
    Returns the name of the seller for which the coupon applies
    """
    def get_seller_name(self):
        seller = User.get(self.seller_id)
        return seller.first_name + " " + seller.last_name

    @staticmethod
    def get(code):
        rows = app.db.execute(
            """
            SELECT code, expiration_date, product_id, seller_id, percent_off
            FROM Coupon
            WHERE code = :code
            """,
            code=code
        )
        if not rows:  # coupon not found
            return None
        return Coupon(*(rows[0]))

    """
    Gets the current valid coupon for the specific product and seller if one exists
    """
    @staticmethod
    def get_current_coupon_for_product_seller(product_id, seller_id):
        rows = app.db.execute(
            """
            SELECT code, expiration_date, product_id, seller_id, percent_off
            FROM Coupon
            WHERE expiration_date >= :now
            AND product_id = :product_id
            """,
            product_id=product_id,
            seller_id=seller_id,
            now=datetime.datetime.now()
        )
        if not rows:  # coupon not found
            return None
        return Coupon(*(rows[0]))

    """
    Generates a new coupon for the specific product and seller. The expiration date is automatically set to 1 week in
    the future and the discount is automatically set to 50% off. THis could be changed to be more flexible in 
    the future
    """
    @staticmethod
    def generate_new_coupon(product_id, seller_id):
        new_code = ''.join(random.choice(letters) for _ in range(random.randint(10, 12)))
        while Coupon.get(new_code):
            new_code = ''.join(random.choice(letters) for _ in range(random.randint(10, 12)))
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=7)

        app.db.execute_with_no_return(
            """
            INSERT INTO Coupon
            VALUES (:code, :expiration_date, :product_id, :seller_id, :percent_off)
            """,
            code=new_code,
            expiration_date=expiration_date,
            product_id=product_id,
            seller_id=seller_id,
            percent_off=PERCENT_OFF
        )

    """
    Returns a random coupon from all valid coupons
    """
    @staticmethod
    def get_random_coupon():
        rows = app.db.execute(
            """
            SELECT code, expiration_date, product_id, seller_id, percent_off
            FROM Coupon
            WHERE expiration_date >= :now
            """,
            now=datetime.datetime.now()
        )
        if not rows:  # coupon not found
            return None
        return Coupon(*(random.choice(rows)))
