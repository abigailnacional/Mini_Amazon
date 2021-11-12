from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request

from .models.cart import Cart
from .models.product_in_cart import ProductInCart
from .models.purchase import Purchase
from .models.user import User


from flask import Blueprint

bp = Blueprint('cart', __name__)


@bp.route('/cart')
def view_cart():
    if current_user.is_authenticated:
        current_cart = Cart.get_current_cart(current_user.id)
        total_price = current_cart.get_total_price_of_cart()

        return render_template(
            'cart.html',
            products_in_cart=current_cart.get_products_in_cart(),
            total_cart_price=total_price
        )
    return redirect(url_for('users.login'))

@bp.route('/order/<cart_id>')
def view_purchased_cart(cart_id):
    if current_user.is_authenticated:
        purchased_cart = Cart.get_cart_by_id(cart_id)
        purchases = purchased_cart.get_purchases_from_cart()
        #total_price = purchased_cart.get_total_price_of_cart() # TODO correct (this would have new prices)

        return render_template(
            'purchase.html',
            products_in_cart=purchased_cart.get_products_in_cart(),
            cart=purchased_cart,
            purchases=purchases,
            total_cart_price=0,
            cart_id=cart_id
        )
    return redirect(url_for('users.login'))

@bp.route('/increase_quantity/<product_in_cart_id>')
def increase_quantity_in_cart(product_in_cart_id):
    if current_user.is_authenticated:
        ProductInCart.increase_quantity(product_in_cart_id)
        return redirect(url_for('cart.view_cart'))
    return redirect(url_for('users.login'))


@bp.route('/decrease_quantity/<product_in_cart_id>')
def decrease_quantity_in_cart(product_in_cart_id):
    if current_user.is_authenticated:

        ProductInCart.decrease_quantity(product_in_cart_id)
        return redirect(url_for('cart.view_cart'))
    return redirect(url_for('users.login'))


@bp.route('/remove_item_from_cart/<product_in_cart_id>')
def remove_item_from_cart(product_in_cart_id):
    if current_user.is_authenticated:
        ProductInCart.remove_from_cart(product_in_cart_id)
        return redirect(url_for('cart.view_cart'))
    return redirect(url_for('users.login'))




# TODO method not complete - currently purchases but does not have any checks for changes to inventory/price or
# TODO to see if user/seller has enough balance/inventory
# TODO must do this as a transaction so that it is atomic
@bp.route('/order_cart')
def order_cart():
    if current_user.is_authenticated:
        current_cart = Cart.get_current_cart(current_user.id)

        if len(current_cart.get_products_in_cart()) == 0:
            print("nothing in cart")
            return redirect(url_for('cart.view_cart'))

        # check that we have enough inventory and balance
        # TODO, handle user not having enough balance
        current_user_account = User.get(current_user.id)
        if not current_user_account.has_enough_money(current_cart.get_total_price_of_cart()):
            print('user does not have enough money')
            return redirect(url_for('cart.view_cart'))
        current_user_account.decrement_balance(total_price=current_cart.get_total_price_of_cart())
            #     return redirect(url_for('cart.view_cart'))
        #for product_in_cart in products_in_cart:
                # TODO, check + handle seller not having enough inventory of product
                #return

        current_cart.convert_cart_to_purchase()
    return redirect(url_for('users.login'))

