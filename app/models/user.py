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
            balance: Optional[int] = 0):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
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
    def register(email, password, first_name, last_name):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, first_name, last_name)
VALUES(:email, :password, :first_name, :last_name)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  first_name=first_name,
                                  last_name=last_name)
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
        rows = app.db.execute("""
SELECT id, email, first_name, last_name
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
