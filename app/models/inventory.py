from flask import current_app as app
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
        """
        Created an inventory entry for units the seller is selling. Displays it as a table with rows. 
        """
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
              AND Sells.is_available = true
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

    
    @staticmethod
    def increase_quantity(product_id: int, seller_id: int):
        """
        Allows seller to increment the number of units they have in their inventory
        """
        app.db.execute_with_no_return(
            """
            UPDATE Sells
            SET inventory = inventory + 1
            WHERE product_id = :product_id
            AND seller_id = :seller_id
            """,

            product_id=product_id,
            seller_id=seller_id
        )

    
    @staticmethod
    def decrease_quantity(product_id: int, seller_id: int):
        """
        Allows seller to decrement the number of units they have in their inventory
        """

        app.db.execute_with_no_return (
            """
            UPDATE Sells
            SET inventory = inventory - 1
            WHERE product_id = :product_id
            AND seller_id = :seller_id
            """,

            product_id=product_id,
            seller_id=seller_id
        )

    @staticmethod
    def set_quantity(product_id: int, new_quantity: int, seller_id: int):
        """
        Allows seller to set the number of units they have in their inventory
        """
        app.db.execute_with_no_return(
            """
            UPDATE Sells
            SET inventory = :new_quantity
            WHERE product_id = :product_id
            AND seller_id = :seller_id
            """,
            new_quantity=new_quantity,
            product_id=product_id,
            seller_id=seller_id
        )

    @staticmethod
    def delete_item(product_id: int, seller_id: int):
        """
        Marks the item as not available, but does not delete the record. 
        Removes item from being visualized on render without needing to reload.
        """
        
        app.db.execute_with_no_return(
            """
            UPDATE Sells
            SET is_available = false
            WHERE product_id = :product_id
            AND seller_id = :seller_id
            """,
            product_id=product_id,
            seller_id=seller_id
        )

    @staticmethod
    def get_amount_available(seller_id, product_id):
        """
        Gets the amount of inventory for a product a seller is selling
        """
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

    
    @staticmethod
    def decrease_seller_inventory_without_commit(conn, product_id, seller_id, quantity):
        """
        This method is used to decrease seller inventory of a product without committing to allow 
        for rollback when purchasing a cart
        """
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


