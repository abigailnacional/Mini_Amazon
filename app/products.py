from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request

from .models.product import Product

from flask import Blueprint
bp = Blueprint('products', __name__)

product_sellers = {'1': 'Beyu Blue', '2': 'The Loop', '3': 'McDonalds', '4': 'Panda Express', '5': 'Il Forno',
                   '6': 'Sazón'}

@bp.route('/product', methods=['GET'])
def view_product():
    vender_id = request.args.get('id')
    products = Product.get_specific(vender_id)
    categories = Product.get_categories()
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories)

@bp.route('/filter', methods=['GET'])
def filtered_view():
    vender_id = request.args.get('id')
    spec_category = request.args.get('cat')
    print(spec_category)
    products = Product.filtered(vender_id, spec_category)
    categories = Product.get_categories()
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories)
    

