from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from sqlalchemy import text

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
            address: Optional[str] = "",
            seller_affiliation: Optional[int] = -1):
            
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.password = password
        self.balance = balance
        self.seller_affiliation = seller_affiliation

    """
    This method is used to confirm if there is a user account with the
    given email and if the given password is the correct password for that
    account.
    """
    @staticmethod
    def get_by_auth(input_email, password):
        rows = app.db.execute("""
SELECT password, id, email, first_name, last_name
FROM Users
WHERE email = :inputted_email
""",
                              inputted_email=input_email)
        if not rows:  # Email does not exist
            return None
        elif not check_password_hash(rows[0][0], password):
            return None
        else:
            return User(*(rows[0][1:]))

    """
    This method is used to confirm if there is a user account with the
    given email.
    """
    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    """
    This method is used to save the information from the registration
    form to the database. Email, first name, last name, and address
    (if one is provided) are saved as is to the database. The password
    is hashed and the hashed version is saved to the database.
    """
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

    """
    This method is used to grab all of the user's info when given a user ID.
    """
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

    """
    This method is used to determine whether the user has enough money
    after a given amount is subtracted from their balance.
    """
    def has_enough_money(self, total_price):
        return app.db.execute(
            """
            SELECT balance
            FROM Users
            WHERE id = :id
            """,
            id=self.id,
        )[0][0] >= total_price

    """
    This method is used to determine whether the user's balance
    will exceed the max int value for SQL after a given amount
    is added to their balance.
    """
    def under_max_balance(self, total_price):
        return app.db.execute(
            """
            SELECT balance
            FROM Users
            WHERE id = :id
            """,
            id=self.id,
        )[0][0] + total_price <= 2147483647 #max int value in SQL

    """
    This method is used to decrease balance without committing to allow for rollback when purchasing a cart
    """
    def decrease_balance_without_commit(self, connection, total_price):
        connection.execute(text(
            """
            UPDATE Users
            SET balance = balance - :total_price
                        WHERE id = :user_id
            """),
            {
                "total_price": total_price,
                "user_id": self.id
            },
        )

    """
    This method is used to increase balance without committing to allow for rollback when purchasing a cart
    """
    def increase_balance_without_commit(self, connection, total_price):
        connection.execute(text(
            """
            UPDATE Users
            SET balance = balance + :total_price
            WHERE id = :user_id
            """),
            {
                "total_price": total_price,
                "user_id": self.id
            },
        )

    """
    This method is used to subtract off a given amount from the user's balance.
    It returns the new balance.
    """
    def decrement_balance(self, amount):
        return app.db.execute(
            """
            UPDATE Users
            SET balance = balance - :amount
            WHERE id = :id
            AND balance >= :amount
            RETURNING*
            """,
            id=self.id,
            amount=amount
        )[0][0]

    """
    This method is used to add a given amount to the user's balance.
    It returns the new balance.
    """
    def increment_balance(self, amount):
        return app.db.execute(
            """
            UPDATE Users
            SET balance = balance + :amount
            WHERE id = :id
            RETURNING*
            """,
            id=self.id,
            amount=amount
        )[0][0]

    """
    This method is used to update the user's email. It returns a boolean
    so that the update can be confirmed.
    """
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

    """
    This method is used to update the user's first name. It returns a boolean
    so that the update can be confirmed.
    """
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

    """
    This method is used to update the user's last name. It returns a boolean
    so that the update can be confirmed.
    """
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

    """
    This method is used to update the user's address. It returns a boolean
    so that the update can be confirmed.
    """
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
        
    """
    This method is used to update the user's password. It returns a boolean
    so that the update can be confirmed.
    """
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

    """
    This method gets all of the users that are sellers and relevant information
    about them.
    """
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

    """
    This method checks if a user is a seller when given a user ID.
    """
    @staticmethod
    def check_seller(id) -> bool:
        rows = app.db.execute(
            """
            SELECT id
            FROM Users
            RIGHT OUTER JOIN Sells ON Users.id=Sells.seller_id
            WHERE id = :id
            """,
            id=id)
        return True if rows else False

    """
    This method gets useful information about ONLY ONE seller when given
    a seller's user ID.
    """
    @staticmethod
    def get_seller_info(id):
        rows = app.db.execute(
            """
            SELECT Users.id, email, first_name, last_name, password, balance, address, seller_affiliation
            FROM Users
            RIGHT OUTER JOIN Sells ON Users.id=Sells.seller_id
            WHERE id = :id
            """,
            id=id)
        return User(*(rows[0])) if rows else None
