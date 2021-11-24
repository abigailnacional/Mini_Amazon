from flask import render_template, redirect, url_for
from flask_login import current_user
from typing import List

import datetime

from .models.inventory import InventoryEntry
# from .models.purchase import Purchase
from .models.coupon import Coupon


from flask import Blueprint

bp = Blueprint('inventory', __name__)


@bp.route('/inventory')
def inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    items: List[InventoryEntry] = InventoryEntry.get_all_entries_by_seller(
        seller_id=current_user.id)

    coupons = {}
    for item in items:
        coupon = Coupon.get_current_coupon_for_product(item.product_id)
        if coupon:
            coupons[item.product_id] = coupon.code

    return render_template(
        'products_sold.html', 
        inventory=items,
        coupons=coupons
    )
