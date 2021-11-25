from flask import current_app as app
# from .product import Product
from typing import List
from sqlalchemy import text


class InventoryEntry:
    """
    Represents one entry in a seller's inventory, corresponding to one type
    of item being sold. 
    """

    def __init__(
        self, 
        seller_affiliation: int,
        seller_id: int, 
        product_id: int, 
        inventory: int,
        name: str,
        category: str,
        price: float,
        is_available: bool
    ):
        self.seller_affiliation = seller_affiliation
        self.seller_id = seller_id
        self.product_id = product_id
        self.inventory = inventory
        self.name = name
        self.category = category
        self.price = price
        self.is_available = is_available

    @staticmethod
    def get_all_entries_by_seller(seller_id: int):
        rows = app.db.execute(
            """
            SELECT Sells.seller_affiliation, Sells.seller_id, Sells.product_id, Sells.inventory,
                   Product.name AS name, 
                   Product.category AS category, 
                   Product.price AS price, 
                   Product.is_available AS is_available
            FROM Sells
            JOIN Product
            ON Product.id=Sells.product_id
            WHERE seller_id = :seller_id
            """,
            seller_id=seller_id
        )

        return [InventoryEntry(
                    seller_affiliation=seller_affiliation,
                    seller_id=seller_id,
                    product_id=product_id,
                    inventory=inventory,
                    name=name,
                    category=category,
                    price=price,
                    is_available=is_available
                ) for (seller_affiliation, 
                       seller_id,
                       product_id,
                       inventory,
                       name, 
                       category, 
                       price, 
                       is_available) in rows]

        
    # TODO: MAKE WAY FOR SELLERS TO ADD PRODUCTS TO THEIR INVENTORY
    # @staticmethod
    # def add_product_to_inventory(seller_id, product_id, inventory):

    #     app.db.execture_non_select_statement(
    #         """
    #         INSERT INTO Sells
    #         VALUES ()
    #         """


    #     )


# Basic requirements:
# A user who wishes to act as a seller will have an inventory page that lists all products for sale by this user. There should be a way to add a product to the inventory. For each product in the user’s inventory, the user can view and change the available quantity for sale by this user, or simply remove it altogether from the inventory.
# A seller can browse/search the history of orders fulfilled or to be fulfilled, sorted by in reverse chronological order by default. For each order in this list, show a summary (buyer information including address, date order placed, total amount/number of items, and overall fulfillment status), but do not show information concerning other sellers (recall that an order may involve multiple sellers), and provide a mechanism for marking a line item as fulfilled. (Recall from Cart / Order that order submission automatically decrements the available quantity in the seller’s inventory; so fulfillment should not further update the inventory.)
# Possible additional features:
# Add visualization/analytics to the inventory and/or order fulfillment pages to show popularity and trends of one’s products.
# Add analytics about buyers who have worked with this seller, e.g., ratings, number of messages, etc.

    @staticmethod
    def get_amount_available(seller_id, product_id):
        return app.db.execute(
            """
            SELECT inventory
            FROM Sells
            WHERE seller_id = :seller_id
            AND product_id = :product_id
            """,
            seller_id=seller_id,
            product_id=product_id
        )[0][0]

    """
    This method is used to decrease seller inventory of a product without committing to allow 
    for rollback when purchasing a cart
    """
    @staticmethod
    def decrease_seller_inventory_without_commit(conn, product_id, seller_id, quantity):
        conn.execute(text(
            """
            UPDATE Sells
            SET inventory = inventory - :quantity
            WHERE seller_id = :seller_id
            AND product_id = :product_id
            """),
            {
                "product_id": product_id,
                "seller_id": seller_id,
                "quantity": quantity
            },
        )


