from flask import render_template, redirect, url_for
from flask_login import current_user
from typing import List
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, TextField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

import datetime

from .models.inventory import InventoryEntry
# from .models.purchase import Purchase

from flask import Blueprint

bp = Blueprint('inventory', __name__)


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
    name = StringField(_l('Product Name'), validators=[DataRequired()])
    description = TextField(_l('Product Description'))
    price = IntegerField(_l('Product Price'), validators=[DataRequired()])
    category = SelectField(_l('Type'),
        choices = [('Entrées', 'Entrées'), ('Sides', 'Sides'), ('Appetizers', 'Appetizers'), ('Desserts', 'Desserts'), ('Beverages', 'Beverages')],
        validators=[DataRequired()]
    )
    restaurant = SelectField(_l('Locations Served'),
        choices = [('Beyu Blue', 'Beyu Blue'), ('The Loop', 'The Loop'), ('McDonalds', 'McDonalds'), ('Panda Express', 'Panda Express'), ('Il Forno', 'Il Forno'), ('Sazon', 'Sazon')],
        validators=[DataRequired()]
    )
    inventory = IntegerField(_l('Product Inventory'), validators=[DataRequired()])
    submit = SubmitField(_l('Post Product'))


@bp.route('/add-product')
def add_product():
    form = AddProductForm()
    return render_template('add_product.html', form=form)



