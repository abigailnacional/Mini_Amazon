from flask import render_template, redirect, url_for
from flask_login import current_user
from typing import List
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, TextField
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
    price = StringField(_l('Product Price'), validators=[DataRequired()])
    category = SelectField(_l('Type'),
        choices = [('Entrées', 'Entrées'), ('Sides', 'Sides'), ('Appetizers', 'Appetizers'), ('Desserts', 'Desserts'), ('Beverages', 'Beverages')],
        validators=[DataRequired()]
    )
    submit = SubmitField(_l('Post product'))


@bp.route('/add-product')
def add_product():
    form = AddProductForm()
    return render_template('add_product.html', form=form)



