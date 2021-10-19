from flask import current_app as app
from .product import Product
from .product_in_cart import ProductInCart
from typing import List, Optional


class Cart:

    def __init__(self, id: int, user_id: int, is_current: bool):
        self.id = id
        self.user_id = user_id
        self.is_current = is_current

    @staticmethod
    def get_products_in_cart(cart_id: int) -> Optional[List[ProductInCart]]:
        rows = app.db.execute(
            """
            SELECT id, product_id, seller_id, quantity
            FROM ProductInCart
            WHERE cart_id = :cart_id
            ORDER BY product_id
            """,
            cart_id=cart_id
        )
        products_in_cart = []
        for product_in_cart_row in rows:
            products_in_cart.append(
                ProductInCart(
                    product_in_cart_row[0],
                    Product.get(product_in_cart_row[1]),
                    cart_id,
                    product_in_cart_row[2],
                    product_in_cart_row[3]
                ))
        return products_in_cart

    @staticmethod
    def get_total_price_of_cart(products_in_cart: List[ProductInCart]) -> int:
        total_price = 0
        for product_in_cart in products_in_cart:
            total_price += product_in_cart.product.price * product_in_cart.quantity
        return total_price

    @staticmethod
    def get_id_of_current_cart(user_id: int) -> Optional[int]:
        rows = app.db.execute(
            """
            SELECT id
            FROM Cart
            WHERE user_id = :user_id
            AND is_current
            """,
            user_id=user_id
        )
        if not rows:  # no cart found for user
            print('no cart for user')
            return None
        return rows[0][0]

    @staticmethod
    def convert_cart_to_purchase(
            user_id,
            cart_id: int,
            products_in_cart: List[ProductInCart]
    ):
        # app.db.execute_non_select_statement(
        #     """
        #         UPDATE Cart
        #         SET is_current = False
        #         WHERE id = :cart_id
        #         """,
        #     cart_id=cart_id,
        # )

        app.db.execute_non_select_statement(
            """
            PREPARE purchase_product_in_cart AS 
            INSERT INTO Purchase(product_in_cart_id, user_id, cart_id) VALUES
            ($1, $2, $3)
            """,
        )

        for product_in_cart in products_in_cart:
            app.db.execute_non_select_statement(
                'EXECUTE purchase_product_in_cart(:product_in_cart_id, :user_id, :cart_id)',
                product_in_cart_id=product_in_cart.id,
                user_id=user_id,
                cart_id=cart_id
            )

        print(app.db.execute("""SELECT * FROM Purchase"""))



# CREATE TABLE Purchase (
#     product_in_cart_id INT NOT NULL PRIMARY KEY,
#     user_id INT NOT NULL,
#     time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
#     is_fulfilled BOOLEAN DEFAULT FALSE,
#     time_of_fulfillment timestamp without time zone DEFAULT NULL,
#     cart_id INT NOT NULL,
#     FOREIGN KEY (cart_id) REFERENCES Cart(id),
#     FOREIGN KEY (user_id) REFERENCES Users(id),
#     FOREIGN KEY (product_in_cart_id) REFERENCES ProductInCart(id)
# );