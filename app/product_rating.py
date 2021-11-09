from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

import time

from app.models.product import Product as p
from app.models.product_review import ProductReview as pr

from flask import Blueprint
bp = Blueprint('product_rating', __name__)

class ProductRatingForm(FlaskForm):
    # product_name = TextAreaField("Product Name", render_kw={'readonly': True})
    number_of_stars = SelectField('Number of stars', choices=[('1', '1 star'),
                                                              ('2', '2 stars'),
                                                              ('3', '3 stars'),
                                                              ('4', '4 stars'),
                                                              ('5', '5 stars')], validators=None)
    written_review = TextAreaField("Written Review", validators=None)
    submit = SubmitField('Submit')

@bp.route('/edit_review', methods=['GET', 'POST'])
def edit_review():
    if current_user.is_authenticated:
        product = p.get("" + request.args.get('product_id'))
        user_id = current_user.id

        review = pr.get_specific_product_review_by_user(user_id, product.id)
        review_form_data = {
            'number_of_stars': review.rating,
            'written_review': review.review
        }
        form = ProductRatingForm(obj=review_form_data)
        
        data = {'product': product}

        return render_template("product_review.html", title='Product Review Form', action="Edit", form=form)
    return redirect(url_for('users.login'))

@bp.route('/create_review', methods=['GET', 'POST'])
def create_review():
    if current_user.is_authenticated:
        form = ProductRatingForm()
        return_message = ""

        product = p.get("" + request.args.get('product_id'))
        user_id = current_user.id

        if form.validate_on_submit():
            num_stars = form.number_of_stars.data
            written_review = form.written_review.data

            #check if reviewer id already exists in database
            if pr.check_user_review_exists(user_id, product.id):
                return_message = "You have already submitted a review for this product!"
                flash(return_message)
                # return redirect(url_for('index.index'))
            else:
                review_contents = {
                    'reviewer_id': user_id, #user_id
                    'rating': int(num_stars),
                    'review': written_review,
                    'product_id': product.id,
                    'seller_id': None,
                    'time_posted': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                pr.add_review(review_contents)

                return redirect(url_for('index.index'))
                
        data = {'product': product}
        return render_template('product_review.html', title='Product Review Form', form=form, data=data, message=return_message)
    return redirect(url_for('users.login'))
