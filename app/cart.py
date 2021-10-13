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
        total_price = 0
        if products_in_cart:
            total_price = Cart.get_total_price_of_cart(products_in_cart)
        return render_template('cart.html', current_cart=products_in_cart, total_cart_price=total_price)
    return render_template('login.html')


@bp.route('/increase_quantity/<cart_id>/<product_id>/<seller_id>')
def increase_quantity_in_cart(cart_id, product_id, seller_id):
    ProductInCart.increase_quantity(cart_id, product_id, seller_id)
    return redirect(url_for('cart.view_cart'))


@bp.route('/decrease_quantity/<cart_id>/<product_id>/<seller_id>')
def decrease_quantity_in_cart(cart_id, product_id, seller_id):
    ProductInCart.decrease_quantity(cart_id, product_id, seller_id)
    return redirect(url_for('cart.view_cart'))

@bp.route('/order_cart')
def order_cart():
    if current_user.is_authenticated:
    # get all items in cart
        current_cart_id = Cart.get_id_of_current_cart(current_user.id)
        products_in_cart = Cart.get_products_in_cart(current_cart_id)
        total_price = Cart.get_total_price_of_cart(products_in_cart)

        # check that we have enough inventory and balance
        # TODO, handle user not having enough balance
        # if User.get(current_user.id).balance < total_price:
        #     print('user does not have enough money')
        #    return
        #for product_in_cart in products_in_cart:
            # TODO, handle seller not having enough inventory of product
            #return

        # TODO, if we have enough inventory and balance, subtract inventory and balance

        # change cart to not current
    # create new cart
    # add to purchase table