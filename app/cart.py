from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request

from .models.cart import Cart
from .models.cart import ProductInCart


from flask import Blueprint

bp = Blueprint('cart', __name__)


@bp.route('/cart')
def view_cart():
    if current_user.is_authenticated:
        current_cart_id = Cart.get_id_of_current_cart(current_user.id)
        products_in_cart = Cart.get_products_in_cart(
            cart_id=current_cart_id
        )
        total_price = Cart.get_total_price_of_cart(current_cart_id)
        return render_template('cart.html', current_cart=products_in_cart, total_cart_price=total_price)
    return render_template('login.html')


@bp.route('/increase_quantity/<cart_id>/<product_id>')
def increase_quantity_in_cart(cart_id, product_id):
    ProductInCart.increase_quantity(cart_id, product_id)
    return redirect(url_for('cart.view_cart'))


@bp.route('/decrease_quantity/<cart_id>/<product_id>')
def decrease_quantity_in_cart(cart_id, product_id):
    ProductInCart.decrease_quantity(cart_id, product_id)
    return redirect(url_for('cart.view_cart'))
