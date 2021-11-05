from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request

from .models.product import Product

from flask import Blueprint
bp = Blueprint('products', __name__)

<<<<<<< HEAD
product_sellers = {'1': 'Beyu Blue', '2': 'The Loop', '3': 'McDonalds', '4': 'Panda Express', '5': 'Il Forno',
                   '6': 'Sazón'}

@bp.route('/product', methods=['GET'])
def view_product():
    seller_id = request.args.get('id')
    products = Product.get_specific(product_sellers[seller_id])
    return render_template('product.html', name=product_sellers[seller_id], avail_products=products)
=======
@bp.route('/product', methods=['GET'])
def view_product():
    seller_id = request.args.get('id')
    return render_template('product.html')
>>>>>>> 8a1301d5d1de20717ad92f9470ef1459f0001fd1

