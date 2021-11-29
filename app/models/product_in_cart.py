from flask import current_app as app
from .product import Product
from .inventory import InventoryEntry
from app.models.coupon import Coupon


class ProductInCart:

    def __init__(
            self,
            id: int,
            product: Product,
            cart_id: int,
            seller_id: int,
            quantity: int
    ):
        self.id = id
        self.product = product
        self.cart_id = cart_id
        self.quantity = quantity
        self.seller_id = seller_id

    def get_total_price_to_pay(self, coupon):
        discount = 0
        if coupon and coupon.product_id == self.product.id and coupon.seller_id == self.seller_id:
            discount = float(self.product.price) * (coupon.percent_off / 100)
        return round((float(self.product.price) * self.quantity) - discount, 2)

    @staticmethod
    def get(product_in_cart_id: int):
        rows = app.db.execute(
            """
            SELECT id, product_id, cart_id, seller_id, quantity
            FROM ProductInCart
            WHERE id = :product_in_cart_id
            """,
            product_in_cart_id=product_in_cart_id
        )[0]

        return ProductInCart(
            id=rows[0],
            product=Product.get(rows[1]),
            cart_id=rows[2],
            seller_id=rows[3],
            quantity=rows[4]
        )

    @staticmethod
    def increase_quantity(product_in_cart_id: int):  # product_in_cart_id refers to the id in the ProductInCart table
        product_in_cart = ProductInCart.get(product_in_cart_id)

        product_amount_available = InventoryEntry.get_amount_available(
            product_in_cart.seller_id,
            product_in_cart.product.id
        )

        if product_in_cart.quantity + 1 <= product_amount_available:
            app.db.execute_with_no_return(
                """
                UPDATE ProductInCart
                SET quantity = quantity + 1
                WHERE id = :id
                """,
                # TODO add upper bound
                id=product_in_cart_id,
            )

    @staticmethod
    def decrease_quantity(product_in_cart_id: int):
        app.db.execute_with_no_return(
            """
            UPDATE ProductInCart
            SET quantity = quantity - 1
            WHERE id = :id
            AND quantity > 1
            """,
            id=product_in_cart_id
        )

    @staticmethod
    def remove_from_cart(product_in_cart_id: int):
        app.db.execute_with_no_return(
            """
            DELETE FROM ProductInCart
            WHERE id = :id
            """,
            id=product_in_cart_id
        )

    @staticmethod
    def add_to_cart(product_id: int, seller_id: int, cart_id):
        rows = app.db.execute(
            """
            SELECT id
            FROM ProductInCart
            WHERE cart_id = :cart_id
            AND seller_id = :seller_id
            AND product_id = :product_id
            """,
            cart_id =cart_id,
            seller_id=seller_id,
            product_id=product_id
        )
        if rows:  # product with same seller already exists in cart
            product_in_cart_id = rows[0][0]
            ProductInCart.increase_quantity(product_in_cart_id)
        else:  # product with this seller must be newly added to cart
            app.db.execute_with_no_return(
                """
                INSERT INTO ProductInCart(cart_id, product_id, seller_id, quantity)
                VALUES (:cart_id, :product_id, :seller_id, :quantity)
                """,
                cart_id=cart_id,
                product_id=product_id,
                seller_id=seller_id,
                quantity=1
            )

