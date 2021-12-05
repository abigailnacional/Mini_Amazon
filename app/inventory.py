import os
from flask import render_template, redirect, url_for, request, flash, Flask, session
from flask_login import current_user
from typing import List
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, TextField, IntegerField, DecimalField, SelectMultipleField, FileField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './app/static/images/products/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

from .models.inventory import InventoryEntry
from .models.coupon import Coupon
from .models.product import Product
# from .models.purchase import Purchase

from flask import Blueprint

bp = Blueprint('inventory', __name__)
bp.config = {}

@bp.route('/inventory', methods=['GET'])
def inventory():
    page_num = int(request.args.get('page'))
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    items: List[InventoryEntry] = InventoryEntry.get_all_entries_by_seller(
        page_num, seller_id=current_user.id)

    coupons = {}
    for item in items:
        coupon = Coupon.get_current_coupon_for_product_seller(item.product_id, item.seller_id)
        if coupon:
            coupons[item.product_id] = coupon.code
    return render_template('products_sold.html', inventory=items, page_num=page_num, max_pages=len(items), coupons=coupons)
    
@bp.route('/inventory/increment_quantity/<id>', methods=['POST'])
def increment_quantity(id):
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    
    InventoryEntry.increase_quantity(id, current_user.id)


    return redirect(url_for('inventory.inventory'))


@bp.route('/inventory/decrement_quantity/<id>', methods=['POST'])
def decrement_quantity(id):
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    
    InventoryEntry.decrease_quantity(id, current_user.id)

    return redirect(url_for('inventory.inventory'))


@bp.route('/inventory/delete_product/<id>', methods=['POST'])
def delete_product(id):
    """
    Marks the Sells.is_available = false for this seller/item.
    """

    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    InventoryEntry.delete_item(id, current_user.id)

    return redirect(url_for('inventory.inventory'))

class AddProductForm(FlaskForm):
    name = StringField(_l('* Product Name'), validators=[DataRequired()])
    description = StringField(_l('Product Description'))
    price = DecimalField(_l('* Product Price'), validators=[DataRequired()])
    category = SelectField(_l('* Type'),
        choices = [('', 'Select a category'), ('Entrées', 'Entrées'), ('Sides', 'Sides'), ('Appetizers', 'Appetizers'), ('Desserts', 'Desserts'), ('Beverages', 'Beverages')],
        validators=[DataRequired()]
    )
    # have to input restaurant id as string for flask form constraints (later convert back to int for sql query)
    restaurant = SelectMultipleField(_l('* Locations Served'),
        choices = [('', 'Select restuarant(s)'), ('1', 'Beyu Blue'), ('2', 'The Loop'), ('3', 'McDonalds'), ('4', 'Panda Express'), ('5', 'Il Forno'), ('6', 'Sazon')],
        validators=[DataRequired()]
    )
    inventory = IntegerField(_l('* Product Inventory'), validators=[DataRequired()])
    image = FileField(_l('* Product Image'), validators=[DataRequired()])
    submit = SubmitField(_l('Start Selling Product'))


@bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if request.method == 'POST':
        image = form.image.data.filename
        if form.validate_on_submit():
            if image.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                f = request.files['image']
                filename = secure_filename(image)
                f.save(os.path.join(UPLOAD_FOLDER, filename))
                prod_id = Product.add_product(form.name.data, form.description.data, form.price.data, form.category.data, form.image.data.filename, current_user)
                for restaurant in form.restaurant.data:
                    InventoryEntry.add_product_to_inventory(current_user, restaurant, prod_id, form.inventory.data)
                return redirect(url_for('inventory.inventory'))
            else:
                flash('Incorrect file type [png, jpg, jpeg accepted]')
                render_template('add_product.html', form=form)
        else:
            return render_template('add_product.html', form=form)
    return render_template('add_product.html', form=form)

class EditProductForm(FlaskForm):
    name = StringField(_l('Product Name'))
    description = StringField(_l('Product Description'))
    price = DecimalField(_l('Product Price'))
    category = SelectField(_l('Type'),
        choices = [('', 'Select a category'), ('Entrées', 'Entrées'), ('Sides', 'Sides'), ('Appetizers', 'Appetizers'), ('Desserts', 'Desserts'), ('Beverages', 'Beverages')]
    )
    # have to input restaurant id as string for flask form constraints (later convert back to int for sql query)
    restaurant = SelectMultipleField(_l('Locations Served'),
        choices = [('', 'Select restuarant(s)'), ('1', 'Beyu Blue'), ('2', 'The Loop'), ('3', 'McDonalds'), ('4', 'Panda Express'), ('5', 'Il Forno'), ('6', 'Sazon')]
    )
    inventory = IntegerField(_l('Product Inventory'))
    image = FileField(_l('Product Image'))
    available = RadioField(_l('Product Avaliability'), choices = [(True, 'Avaliable'), (False, 'Not avaliable')])
    submit = SubmitField(_l('Update Product Info'))

@bp.route('/edit-product', methods=['GET', 'POST'])
def edit_product():
    form = EditProductForm()
    product_id = int(request.args.get('product_id'))
    if request.method == 'POST':
        image = form.image.data.filename
        # product image is being changed    
        if image != "":
            if image.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                f = request.files['image']
                filename = secure_filename(image)
                f.save(os.path.join(UPLOAD_FOLDER, filename))
            # product image submitted is wrong file type
            else:
                flash('Incorrect file type [png, jpg, jpeg accepted]')

        if form.name.data != "":
            Product.update_name(product_id, form.name.data)
            return redirect(url_for('inventory.inventory', page=1))
        if form.description.data != "":
            Product.update_description(product_id, form.description.data)
            return redirect(url_for('inventory.inventory', page=1))
        if form.price.data != None:
            Product.update_price(product_id, form.price.data)
            return redirect(url_for('inventory.inventory', page=1))
        if form.category.data != "":
            Product.update_category(product_id, form.category.data)
            return redirect(url_for('inventory.inventory', page=1))
        if form.restaurant.data != "":
            for restaurant in form.restaurant.data:
                InventoryEntry.update_restaurant(current_user, product_id, restaurant)
                return redirect(url_for('inventory.inventory', page=1))
        if form.inventory.data != None:
            InventoryEntry.update_inventory(current_user, product_id, form.inventory.data)
            return redirect(url_for('inventory.inventory', page=1))
        if form.available.data != None:
            Product.update_availability(product_id, form.available.data)
            return redirect(url_for('inventory.inventory', page=1))
        else:
            return render_template('edit_product.html', form=form)
    return render_template('edit_product.html', form=form)



