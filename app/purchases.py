from flask import Blueprint
from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request

from .models.cart import Cart
from .models.product_in_cart import ProductInCart
from .models.user import User
from .models.purchase import Purchase



bp = Blueprint('purchases', __name__)


@bp.route('/purchases')
def view_cart():
    if current_user.is_authenticated:
        current_cart = Cart.get_current_cart(current_user.id)
        total_price = current_cart.get_total_price_of_cart()

        Purchase.get_all_purchases(current_user.id)
        return render_template(
            'purchases.html',
            products_in_cart=current_cart.get_products_in_cart(),
            total_cart_price=total_price
        )
    return redirect(url_for('users.login'))