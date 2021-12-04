from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request

from .models.product import Product
from .models.product_review import ProductReview
from .models.user import User

from flask import Blueprint
bp = Blueprint('products', __name__)

product_sellers = {1: 'Beyu Blue', 2: 'The Loop', 3: 'McDonalds', 4: 'Panda Express', 5: 'Il Forno',
                   6: 'Sazón'}

@bp.route('/product', methods=['GET'])
def view_product():
    vender_id = int(request.args.get('id'))
    products = Product.get_specific(vender_id)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_product_average_rating([product.id for product in products])
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings)

@bp.route('/filter', methods=['GET'])
def filtered_cat():
    vender_id = int(request.args.get('id'))
    spec_category = request.args.get('cat')
    products = Product.filteredCat(vender_id, spec_category)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_product_average_rating([product.id for product in products])
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings)

@bp.route('/filter-price', methods=['GET'])
def filtered_price():
    vender_id = int(request.args.get('id'))
    products = Product.filteredPrice()
    categories = Product.get_categories()
    average_ratings = ProductReview.get_product_average_rating([product.id for product in products])
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings)  

@bp.route('/search', methods=['GET'])
def search_filter():
    vender_id = int(request.args.get('id'))
    search = request.args.get('search')
    products = Product.search_filter(search)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_product_average_rating([product.id for product in products])
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings)  

@bp.route('/id-search', methods=['GET'])
def search_id():
    vender_id = int(request.args.get('id'))
    search = request.args.get('search')
    products = Product.search_id(search)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_product_average_rating([product.id for product in products])
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings)  

@bp.route('/view', methods=['GET'])
def ind_view():
    prod_id = int(request.args.get('id'))
    product = Product.get(prod_id)
    sellers = User.get_sellers(prod_id)
    reviews = ProductReview.get_reviews(prod_id, "product")
    summary_ratings = ProductReview.get_summary_rating(prod_id, "product")
    return render_template('ind_prod.html', product_info=product, sellers=sellers, 
                            product_sellers=product_sellers, reviews=reviews, summary_ratings=summary_ratings)
    

