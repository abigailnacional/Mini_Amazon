from datetime import datetime
from flask import current_app as app
import string
import random
import datetime

letters = string.ascii_lowercase

class Coupon:

    def __init__(
            self,
            code: str,
            expiration_date: datetime,
            product_id: int,
            percent_off: float,
    ):
        self.code = code
        self.expiration_date = expiration_date
        self.product_id = product_id
        self.percent_off = percent_off

    def is_expired(self):
        return datetime.datetime.now() <= self.expiration_date

    @staticmethod
    def get(code):
        rows = app.db.execute(
            """
            SELECT code, expiration_date, product_id, percent_off
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
            SELECT code, expiration_date, product_id, percent_off
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
    def generate_new_coupon(product_id):
        new_code = ''.join(random.choice(letters) for _ in range(random.randint(10, 12)))
        while Coupon.get(new_code):
            new_code = ''.join(random.choice(letters) for _ in range(random.randint(10, 12)))
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=7)
        percent_off = random.randint(1, 100)

        app.db.execute_with_no_return(
            """
            INSERT INTO Coupon
            VALUES (:code, :expiration_date, :product_id, :percent_off)
            """,
            code=new_code,
            expiration_date=expiration_date,
            product_id=product_id,
            percent_off=percent_off
        )

