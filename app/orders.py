from app.models.purchase import Purchase
from flask_login import current_user
from flask import render_template, redirect, url_for, request

from .models.cart import Cart

from flask import Blueprint

bp = Blueprint('order', __name__)


@bp.route('/view_orders')
def view_orders():
    """
    This method fetches all purchased carts for the current user
    """

    if current_user.is_authenticated:
        page_num = int(request.args.get('page', default=1))

        # need all past carts
        purchased_carts = Cart.get_purchased_carts(current_user.id, page_num)

        return render_template(
            'orders.html',
            purchased_carts=purchased_carts,
            page_num=page_num
        )
    return redirect(url_for('users.login'))


@bp.route('/incoming_orders', methods=['GET'])
def incoming_orders():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    orders = Purchase.get_seller_incoming_orders(current_user.id)

    return render_template(
            'incoming_orders.html',
            incoming_orders=orders)

@bp.route('/fulfilled_orders', methods=['GET'])
def fulfilled_orders():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    orders = Purchase.get_seller_fulfilled_orders(current_user.id)

    return render_template(
            'fulfilled_orders.html',
            fulfilled_orders=orders)


@bp.route('/order/fulfill/<id>/<cart_id>', methods=['POST'])
def fulfill(id, cart_id):
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    
    Purchase.mark_as_fulfilled(id, cart_id)

    return redirect(url_for('order.incoming_orders'))
