from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional

from .. import login


class User(UserMixin):
    def __init__(
            self,
            id: int,
            email: str,
            first_name: str,
            last_name:  str,
            password: Optional[str] = "",
            balance: Optional[int] = 0,
            address: Optional[str] = ""):
            
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.password = password
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, first_name, last_name
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        # second check allows us to use the preloaded csv data (remove at some point)
        elif not check_password_hash(rows[0][0], password) \
                and not check_password_hash(generate_password_hash(rows[0][0]), password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, first_name, last_name, address):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, first_name, last_name, address)
VALUES(:email, :password, :first_name, :last_name, :address)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  first_name=first_name,
                                  last_name=last_name,
                                  address=address)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            print("except!", e)
            # likely email already in use; better error checking and
            # reporting needed
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute(
            """
            SELECT id, email, first_name, last_name, password, balance, address
            FROM Users
            WHERE id = :id
            """,
            id=id)
        return User(*(rows[0])) if rows else None

    def has_enough_money(self, total_price):
        return app.db.execute(
            """
            SELECT balance
            FROM Users
            WHERE id = :id
            """,
            id=self.id,
        )[0][0] >= total_price

    def decrement_balance(self, total_price):
        app.db.execute_with_no_return(
            """
            UPDATE Users
            SET balance = balance - :total_price
            WHERE id = :id
            AND balance > :total_price
            """,
            id=self.id,
            total_price=total_price
        )

#The function below is just the same as the one above except it returns rows.
#I created it to avoid potential merge conflicts that would
#   result from changing the use of the top function in files related to Cart.
#TODO: Combine the functions above and below this comment block.

    def decrement_balance2(self, total_price):
        return app.db.execute(
            """
            UPDATE Users
            SET balance = balance - :total_price
            WHERE id = :id
            AND balance > :total_price
            RETURNING*
            """,
            id=self.id,
            total_price=total_price
        )[0][0]

    def increment_balance(self, total_price):
        return app.db.execute(
            """
            UPDATE Users
            SET balance = balance + :total_price
            WHERE id = :id
            RETURNING*
            """,
            id=self.id,
            total_price=total_price
        )[0][0]

    def edit_email(self, email) -> bool:
        return app.db.execute(
            """
            UPDATE Users
            SET email = :email
            WHERE id = :id
            RETURNING email
            """,
            id=self.id,
            email=email,
        )[0][0] == email

    def edit_fname(self, first_name) -> bool:
        return app.db.execute(
            """
            UPDATE Users
            SET first_name = :first_name
            WHERE id = :id
            RETURNING first_name
            """,
            id=self.id,
            first_name=first_name,
        )[0][0] == first_name

    def edit_lname(self, last_name) -> bool:
        return app.db.execute(
            """
            UPDATE Users
            SET last_name = :last_name
            WHERE id = :id
            RETURNING last_name
            """,
            id=self.id,
            last_name=last_name,
        )[0][0] == last_name

    def edit_address(self, address) -> bool:
        return app.db.execute(
            """
            UPDATE Users
            SET address = :address
            WHERE id = :id
            RETURNING address
            """,
            id=self.id,
            address = address
        )[0][0] == address
        
    def edit_password(self, password) -> bool:
        return app.db.execute(
            """
            UPDATE Users
            SET password = :password
            WHERE id = :id
            RETURNING id
            """,
            id=self.id,
            password = generate_password_hash(password)
        )[0][0] == self.id

    def edit_balance(self, balance) -> bool:
        return app.db.execute(
            """
            UPDATE Users
            SET balance = :balance
            WHERE id = :id
            RETURNING balance
            """,
            id=self.id,
            balance = balance
        )[0][0] == balance

    @staticmethod
    def get_sellers(id):
        rows = app.db.execute('''
SELECT id, first_name, last_name, email, inventory, seller_affiliation
FROM Users
RIGHT OUTER JOIN Sells ON Users.id=Sells.seller_id
WHERE product_id = :id
''',
                            id=id)     
        return  rows if rows is not None else None 