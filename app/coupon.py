from flask_login import current_user
from flask import redirect, url_for

from .models.coupon import Coupon
from flask import Blueprint


bp = Blueprint('coupon', __name__)


@bp.route('/generate_coupon/<product_id>/<seller_id>')
def generate_coupon(product_id, seller_id):
    if current_user.is_authenticated:
        if not Coupon.get_current_coupon_for_product(product_id):
            Coupon.generate_new_coupon(product_id, seller_id)
        return redirect(url_for('inventory.inventory'))
    return redirect(url_for('users.login'))
