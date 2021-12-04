import os
from flask import render_template, redirect, url_for, request, flash, Flask
from flask_login import current_user
from typing import List
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, TextField, IntegerField, DecimalField, SelectMultipleField, FileField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './app/static/images/products/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

import datetime

from .models.inventory import InventoryEntry
from .models.product import Product
# from .models.purchase import Purchase

from flask import Blueprint

bp = Blueprint('inventory', __name__)
bp.config = {}

@bp.route('/inventory')
def inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    items: List[InventoryEntry] = InventoryEntry.get_all_entries_by_seller(
        seller_id=current_user.id)

    return render_template(
        'products_sold.html', 
        inventory=items)

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
    global base
    form = AddProductForm()
    if request.method == 'POST':
        image = form.image.data.filename
        if form.validate_on_submit():
            if image.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                f = request.files['image']
                filename = secure_filename(image)
                f.save(os.path.join(UPLOAD_FOLDER, filename))
                prod_id = Product.add_product(form.name.data, form.description.data, form.price.data, form.category.data, form.image.data.filename, current_user)
                print(prod_id)
                for restaurant in form.restaurant.data:
                    InventoryEntry.add_product_to_inventory(current_user, restaurant, prod_id, form.inventory.data)
                return redirect(url_for('inventory.inventory'))
            else:
                flash('Incorrect file type [png, jpg, jpeg accepted]')
                render_template('add_product.html', form=form)
        else:
            return render_template('add_product.html', form=form)
    return render_template('add_product.html', form=form)




