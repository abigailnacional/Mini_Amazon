from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

from app.models.product import Product as p

from flask import Blueprint
bp = Blueprint('product_rating', __name__)

class ProductRatingForm(FlaskForm):
    number_of_stars = StringField('Number of stars', [DataRequired()])
    written_review = TextField("Written Review")
    submit = SubmitField('Submit')


@bp.route('/create_review', methods=['GET', 'POST'])
def create_review():
    form = ProductRatingForm()
    product_id = request.args.get('product_id')
    product = p.get("" + product_id)

    data = {'product': product}

    return render_template('product_review.html', title='Product Review Form', form=form, data=data) # TODO: create a form directly?
