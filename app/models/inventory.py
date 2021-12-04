from flask import current_app as app
# from .product import Product
from typing import List


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
    def get_all_entries_by_seller(page_num, seller_id: int):
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
            LIMIT 20
            OFFSET ((:page_num - 1) * 20)
            """,
            seller_id=seller_id,
            page_num=page_num
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

    @staticmethod
    def add_product_to_inventory(current_seller, restaurant, product_id, inventory):

        rows = app.db.execute_with_no_return('''
    INSERT INTO Sells (seller_affiliation, seller_id, product_id, inventory)
    VALUES (:restaurant, :seller_id, :product_id, :inventory);
        ''',
            restaurant=restaurant,
            seller_id=current_seller.id,
            product_id=product_id,
            inventory=inventory)


# Basic requirements:
# A user who wishes to act as a seller will have an inventory page that lists all products for sale by this user. There should be a way to add a product to the inventory. For each product in the user’s inventory, the user can view and change the available quantity for sale by this user, or simply remove it altogether from the inventory.
# A seller can browse/search the history of orders fulfilled or to be fulfilled, sorted by in reverse chronological order by default. For each order in this list, show a summary (buyer information including address, date order placed, total amount/number of items, and overall fulfillment status), but do not show information concerning other sellers (recall that an order may involve multiple sellers), and provide a mechanism for marking a line item as fulfilled. (Recall from Cart / Order that order submission automatically decrements the available quantity in the seller’s inventory; so fulfillment should not further update the inventory.)
# Possible additional features:
# Add visualization/analytics to the inventory and/or order fulfillment pages to show popularity and trends of one’s products.
# Add analytics about buyers who have worked with this seller, e.g., ratings, number of messages, etc.
