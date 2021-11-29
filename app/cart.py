from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_babel import _, lazy_gettext as _l


from .models.cart import Cart
from .models.product_in_cart import ProductInCart
from .models.product import Product
from .models.purchase import Purchase
from .inventory import InventoryEntry
from .models.user import User
from .models.coupon import Coupon
from .errors import *
import datetime

from flask import Blueprint

bp = Blueprint('cart', __name__)


class AddCouponForm(FlaskForm):
    coupon_code = StringField(_l('Coupon Code'), validators=[DataRequired()])
    submit = SubmitField(_l('Add Coupon Code'))


@bp.route('/cart', methods=['GET', 'POST'])
def view_cart():
    if current_user.is_authenticated:
        current_cart = Cart.get_current_cart(current_user.id)
        total_price = current_cart.get_total_current_price(None)
        form = AddCouponForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                coupon = Coupon.get(form.coupon_code.data)
                if not coupon:
                    flash(COUPON_DOES_NOT_EXIST)
                elif coupon.expiration_date < datetime.datetime.now():
                    flash(COUPON_EXPIRED.format(coupon.code))
                elif not current_cart.is_product_by_seller_in_cart(coupon.product_id, coupon.seller_id):
                    flash(COUPON_FOR_ITEM_NOT_IN_CART.format(coupon.code, coupon.product_id, coupon.seller_id))
                else:
                    flash(COUPON_SUCCESSFUL.format(coupon.code, coupon.percent_off, coupon.product_id,
                                                   coupon.seller_id))
                    total_price = current_cart.get_total_current_price(coupon)
                    current_cart.add_coupon(coupon.code)
        else:
            coupon = Coupon.get(current_cart.coupon_applied)
            if coupon:
                flash(COUPON_SUCCESSFUL.format(coupon.code, coupon.percent_off, coupon.product_id, coupon.seller_id))
                total_price = current_cart.get_total_current_price(coupon)

        return render_template(
            'cart.html',
            products_in_cart=current_cart.get_products_in_cart(),
            total_cart_price=total_price,
            user_can_order=total_price <= User.get(current_user.id).balance,
            form=form
        )

    return redirect(url_for('users.login'))


@bp.route('/order/<cart_id>')
def view_purchased_cart(cart_id):
    if current_user.is_authenticated:

        purchased_cart = Cart.get_cart_by_id(cart_id)
        purchases = purchased_cart.get_purchases()
        coupon = None
        if purchased_cart.coupon_applied:
            coupon = Coupon.get(purchased_cart.coupon_applied)

        final_price = 0
        for purchase in purchases:
            final_price += purchase.get_total_price_paid(coupon)


        return render_template(
            'purchase.html',
            products_in_cart=purchased_cart.get_products_in_cart(),
            cart=purchased_cart,
            purchases=purchases,
            total_cart_price=final_price,
            cart_id=cart_id,
            coupon=coupon
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


"""
This method converts a cart into a purchase by:
    for each product in the cart,
    1) validating the buyer has enough money 
    2) validating the seller has enough inventory
    3) subtracting from the buyer's balance
    4) adding to the seller's balance
    5) subtracting from the seller's inventory
    6) adding the product to purchases
Finally, the cart is marked purchased and a new cart is created for the user

This method calls some methods that may seem repeated, but this is necessary because these methods must run as part of a 
transaction in order to rollback if the user runs out of money or a seller runs out of inventory. Since the SQL
in our codebase is automatically committed in all other places, some methods used here must be repetitive. 
"""
@bp.route('/order_cart')
def order_cart():

    if current_user.is_authenticated:
        current_cart = Cart.get_current_cart(current_user.id)

        if len(current_cart.get_products_in_cart()) == 0:
            flash("You have nothing in your cart!")
            return redirect(url_for('cart.view_cart'))

        with app.db.engine.begin() as conn:

            for product_in_cart in current_cart.get_products_in_cart():  # TODO need to add final prices somehow

                # get product price
                total_product_price = product_in_cart.get_total_price_to_pay(Coupon.get(current_cart.coupon_applied))

                # ensure user has enough money
                user_has_enough_money = User.get(current_user.id).balance >= total_product_price
                if not user_has_enough_money:
                    flash(NOT_ENOUGH_MONEY)
                    conn.rollback()
                    return redirect(url_for('cart.view_cart'))

                # ensure seller has enough inventory
                seller_product_inventory = InventoryEntry.get_amount_available(
                    product_in_cart.seller_id,
                    product_in_cart.product.id
                )
                seller_has_enough_inventory = product_in_cart.quantity <= seller_product_inventory
                if not seller_has_enough_inventory:
                    flash(NOT_ENOUGH_INVENTORY.format(product_in_cart.product.id))
                    conn.rollback()
                    return redirect(url_for('cart.view_cart'))

                # take from buyer balance
                User.get(current_user.id).decrease_balance_without_commit(conn, total_product_price)
                # take from seller inventory
                InventoryEntry.decrease_seller_inventory_without_commit(
                    conn,
                    product_in_cart.product.id,
                    product_in_cart.seller_id,
                    product_in_cart.quantity
                )
                # add to seller balance
                User.get(product_in_cart.seller_id).increase_balance_without_commit(conn, total_product_price)

                # add purchase for user
                Purchase.insert_new_purchase_without_commit(
                    conn,
                    product_in_cart.id,
                    current_user.id,
                    current_cart.id,
                    product_in_cart.product.price
                )

            conn.commit()
            current_cart.mark_as_purchased()
            Cart.create_new_cart(current_user.id)
            return redirect(url_for('order.view_orders'))
    return redirect(url_for('users.login'))

