from flask_login import current_user
from flask import render_template, redirect, url_for, request

from .models.cart import Cart

from flask import Blueprint

bp = Blueprint('order', __name__)

"""
This method fetches all purchased carts for the current user
"""
@bp.route('/view_orders')
def view_orders():
    if current_user.is_authenticated:
        page_num = int(request.args.get('page'))

        # need all past carts
        purchased_carts = Cart.get_purchased_carts(current_user.id, page_num)

        return render_template(
            'orders.html',
            purchased_carts=purchased_carts,
            page_num=page_num
        )
    return redirect(url_for('users.login'))
