from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request

from .models.product import Product

from flask import Blueprint
bp = Blueprint('products', __name__)

@bp.route('/product', methods=['GET'])
def view_product():
    seller_id = request.args.get('id')
    return render_template('product.html')

