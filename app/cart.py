from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request, get_flashed_messages

from .models.cart import Cart
from .models.product_in_cart import ProductInCart
from .models.user import User
from .models.coupon import Coupon
from .errors import COUPON_DOES_NOT_EXIST, COUPON_SUCCESSFUL


from flask import Blueprint

bp = Blueprint('cart', __name__)


@bp.route('/cart')
def view_cart():
    if current_user.is_authenticated:
        current_cart = Cart.get_current_cart(current_user.id)
        total_price = current_cart.get_total_current_price()

        return render_template(
            'cart.html',
            products_in_cart=current_cart.get_products_in_cart(),
            total_cart_price=total_price,
            user_can_order=total_price <= User.get(current_user.id).balance
        )
    return redirect(url_for('users.login'))

@bp.route('/order/<cart_id>')
def view_purchased_cart(cart_id):
    if current_user.is_authenticated:
        purchased_cart = Cart.get_cart_by_id(cart_id)
        purchases = purchased_cart.get_purchases()

        final_price = 0
        for purchase in purchases:
            final_price += purchase.final_unit_price * purchase.product_in_cart.quantity


        return render_template(
            'purchase.html',
            products_in_cart=purchased_cart.get_products_in_cart(),
            cart=purchased_cart,
            purchases=purchases,
            total_cart_price=final_price,
            cart_id=cart_id
        )
    return redirect(url_for('users.login'))

@bp.route('/add_item_to_cart/<product_id>/<seller_id>')
def add_item_to_cart(product_id, seller_id):
    if current_user.is_authenticated:
        current_cart_id = Cart.get_id_of_current_cart(current_user.id)
        ProductInCart.add_to_cart(product_id, seller_id, current_cart_id)
        return redirect(request.referrer)
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
            flash("You have nothing in your cart!")
            return redirect(url_for('cart.view_cart'))

        # total_price = current_cart.get_total_price()
        # if total_price > User.get(current_user.id).balance:
        #     flash(NOT_ENOUGH_MONEY)
        #     return redirect(url_for('cart.view_cart'))

        # check that we have enough inventory and balance
        # TODO, handle user not having enough balance
        #current_user_account = User.get(current_user.id)
        # if not current_user_account.has_enough_money(current_cart.get_total_price_of_cart()):
        #     print('user does not have enough money')
        #     return redirect(url_for('cart.view_cart'))
       # current_user_account.decrement_balance(total_price=current_cart.get_total_price_of_cart())
            #     return redirect(url_for('cart.view_cart'))
        #for product_in_cart in products_in_cart:
                # TODO, check + handle seller not having enough inventory of product
                #return

        was_cart_purchase_successful = current_cart.convert_cart_to_purchase()
        if not was_cart_purchase_successful:
            return redirect(url_for('cart.view_cart'))
    return redirect(url_for('order.view_orders'))

@bp.route('/apply_coupon')
def apply_coupon(coupon_code):
    if current_user.is_authenticated:
        coupon = Coupon.get(coupon_code)
        if not coupon:
            flash(COUPON_DOES_NOT_EXIST)
        else:
            flash(COUPON_SUCCESSFUL.format(coupon.percent_off, coupon.product_id))
