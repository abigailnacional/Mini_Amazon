from flask import current_app as app
from typing import Optional
from .user import User

class Seller():
    def __init__(
            self,
            id: int,
            email: str,
            first_name: str,
            last_name:  str,
            seller_affiliation: int,
            address: Optional[str] = "",            
            password: Optional[str] = "",
            balance: Optional[int] = 0):
            
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.seller_affiliation = seller_affiliation
        self.address = address
        self.password = password
        self.balance = balance        

    @staticmethod
    def get_seller_info(id) -> "Seller":
        rows = app.db.execute(
            """
            SELECT id, email, first_name, last_name, seller_affiliation, address
            FROM Users
            RIGHT OUTER JOIN Sells ON Users.id=Sells.seller_id
            WHERE id = :id
            """,
            id=id)
        return Seller(*(rows[0])) if rows else None