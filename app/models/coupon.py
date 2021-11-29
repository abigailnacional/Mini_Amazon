from datetime import datetime
from flask import current_app as app
import string
import random
import datetime

letters = string.ascii_lowercase
PERCENT_OFF = 50 # currently a constant half off, but could change in the future

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

    def is_expired(self):
        return datetime.datetime.now() <= self.expiration_date

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

    @staticmethod
    def get_current_coupon_for_product(product_id):
        rows = app.db.execute(
            """
            SELECT code, expiration_date, product_id, seller_id, percent_off
            FROM Coupon
            WHERE expiration_date >= :now
            AND product_id = :product_id
            """,
            product_id=product_id,
            now=datetime.datetime.now()
        )
        if not rows:  # coupon not found
            return None
        return Coupon(*(rows[0]))

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

    @staticmethod
    def get_random_coupon_code():
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
