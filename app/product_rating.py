from flask import render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

import time

from app.models.product import Product as p

from flask import Blueprint
bp = Blueprint('product_rating', __name__)

class ProductRatingForm(FlaskForm):
    number_of_stars = SelectField('Number of stars', choices=[(1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')], validators=[DataRequired()])
    written_review = TextAreaField("Written Review", validators=[DataRequired()])
    submit = SubmitField('Submit')


@bp.route('/create_review', methods=['GET', 'POST'])
def create_review():
    form = ProductRatingForm()
    return_message = ""

    product = p.get("" + request.args.get('product_id'))
    user_id = '111'

    print("roched")

    if form.validate_on_submit():
        print("reacyhed")
        num_stars = form.number_of_stars.data
        written_review = form.written_review.data

        #check if reviewer id already exists in database
        if p.check_user_review_exists:
            return_message = "You have already submitted a review for this product!"
        else:
            review_contents = {
                'reviewer_id': user_id, #user_id
                'rating': int(num_stars),
                'review': written_review,
                'product_id': product,
                'seller_id': 'N/A',
                'time_posted': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            p.add_review(review_contents)

            return redirect(url_for('actor', id=id)) # TODO: redirect to product page (index)
    else:
        print("manned")
            
    data = {'product': product}
    return render_template('product_review.html', title='Product Review Form', form=form, data=data, message=return_message)
