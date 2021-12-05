from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

import time

from app.models.product import Product as p
from app.models.product_review import ProductReview as pr
from app.models.user import User as u

from flask import Blueprint
bp = Blueprint('product_rating', __name__)

class CreateReviewForm(FlaskForm):
    number_of_stars = SelectField('Number of stars', choices=[('1', '1 star'),
                                                              ('2', '2 stars'),
                                                              ('3', '3 stars'),
                                                              ('4', '4 stars'),
                                                              ('5', '5 stars')], validators=None)
    written_review = TextAreaField("Written Review", validators=None)
    submit = SubmitField('Submit')

@bp.route('/view_reviews')
def view_reviews():
    if current_user.is_authenticated:
        reviews = pr.get_reviews_by_user(current_user.id)

        product_reviews, reviewed_product_ids, reviewed_product_names = [], [], []
        seller_reviews, reviewed_seller_ids, reviewed_seller_names = [], [], []

        for review in reviews:
            if review.product_id != -1:
                reviewed_product_names.append(p.get(review.product_id).name)
                reviewed_product_ids.append(review.product_id)
                product_reviews.append(review)
            else:
                reviewed_seller_names.append(u.get(review.seller_id).first_name + " " + u.get(review.seller_id).last_name)
                reviewed_seller_ids.append(review.seller_id)
                seller_reviews.append(review)

        return render_template('reviews.html', product_names=reviewed_product_names, 
                                               product_ids=reviewed_product_ids,
                                               seller_names=reviewed_seller_names, 
                                               seller_ids=reviewed_seller_ids,
                                               product_reviews=product_reviews,
                                               seller_reviews=seller_reviews)
    return redirect(url_for('users.login'))

@bp.route('/edit_review', methods=['GET', 'POST'])
def edit_review():
    if current_user.is_authenticated:
        review_type = request.args.get('review_type')
        id = request.args.get('id')
        review_obj = p.get(id) if review_type == "product" else u.get(id)
        user_id = current_user.id

        review = pr.get_specific_review_by_user(user_id, id, review_type)

        form = CreateReviewForm(number_of_stars=review.rating, written_review=review.review)

        if form.validate_on_submit():
            num_stars = form.number_of_stars.data
            written_review = form.written_review.data

            edit_review_contents = {
                'reviewer_id': user_id, #user_id
                'rating': int(num_stars),
                'review': written_review,
                'product_id': int(id) if review_type == "product" else -1,
                'seller_id': int(id) if review_type == "seller" else -1,
                'time_posted': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            pr.update_review(edit_review_contents)

            return redirect(url_for('index.index'))

        data = {
            'review_type': review_type,
            'review_obj': review_obj
        }

        return render_template("create_review.html", title='Product Review Form', action="Edit", form=form, data=data, message="")
    return redirect(url_for('users.login'))

@bp.route('/remove_review', methods=['GET', 'POST'])
def remove_review():
    if current_user.is_authenticated:
        review_type = request.args.get('review_type')
        id = request.args.get('id')
        user_id = current_user.id

        pr.remove_specific_review_by_user(user_id, id, review_type)

        return redirect(request.referrer)
    return redirect(url_for('users.login'))

@bp.route('/upvote_review')
def upvote_review():
    if current_user.is_authenticated:
        reviewer_id = request.args.get('reviewer_id')
        review_type = request.args.get('review_type')
        id = request.args.get('id')
        user_id = current_user.id

        reviewer_id = reviewer_id
        upvoter_id = user_id
        product_id = int(id) if review_type == "product" else -1
        seller_id = int(id) if review_type == "seller" else -1

        pr.upvote_review(upvoter_id, reviewer_id, product_id, seller_id)

        return redirect(request.referrer)
    return redirect(url_for('users.login'))

@bp.route('/remove_upvote')
def remove_upvote():
    if current_user.is_authenticated:
        reviewer_id = request.args.get('reviewer_id')
        review_type = request.args.get('review_type')
        id = request.args.get('id')
        user_id = current_user.id

        upvoter_id = user_id
        reviewer_id = reviewer_id
        product_id = int(id) if review_type == "product" else -1
        seller_id = int(id) if review_type == "seller" else -1

        if pr.check_upvote_exists(upvoter_id, reviewer_id, product_id, seller_id):
            pr.remove_upvote(upvoter_id, reviewer_id, product_id, seller_id)
        else:
            flash("This upvote doesn't exist!")

        return redirect(request.referrer)
    return redirect(url_for('users.login'))

@bp.route('/report_review')
def report_review():
    if current_user.is_authenticated:
        reviewer_id = request.args.get('reviewer_id')
        review_type = request.args.get('review_type')
        id = request.args.get('id')
        user_id = current_user.id

        reporter_id = user_id
        reviewer_id = reviewer_id
        product_id = int(id) if review_type == "product" else -1
        seller_id = int(id) if review_type == "seller" else -1

        if pr.check_report_exists(user_id, reviewer_id, product_id, seller_id):
            flash("You cannot report your own review! If there is a problem, remove it instead.")
        else:
            pr.report_review(reporter_id, reviewer_id, product_id, seller_id)
        
        return redirect(request.referrer)

    return redirect(url_for('users.login'))

@bp.route('/create_review', methods=['GET', 'POST'])
def create_review():
    if current_user.is_authenticated:
        form = CreateReviewForm()
        return_message = ""
        review_type = request.args.get('review_type')
        id = request.args.get('id')
        # There can only either be product reviews or seller (user) reviews
        review_obj = p.get(id) if review_type == "product" else u.get(id)
        user_id = current_user.id

        if form.validate_on_submit():
            num_stars = form.number_of_stars.data
            written_review = form.written_review.data

            #check if reviewer id already exists in database
            # TODO: move this code to before user fills out data
            if pr.check_user_review_exists(user_id, id, review_type):
                return_message = "You have already submitted a review for this " + review_type + "!"
                flash(return_message)
                # return redirect(url_for('index.index'))
            elif review_type == "seller" and not pr.check_user_can_review_seller(user_id, id):
                flash("You cannot create a review because you have not ordered anything from this seller yet!")
            else:
                create_review_contents = {
                    'reviewer_id': user_id,
                    'rating': int(num_stars),
                    'review': written_review,
                    'product_id': int(id) if review_type == "product" else -1, #temp fix for db cols not accepting NULL values
                    'seller_id': int(id) if review_type == "seller" else -1,
                    'time_posted': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'upvotes': 0,
                    'reports': 0
                }

                pr.add_review(create_review_contents)

                return redirect(url_for('index.index'))
                
        data = {
            'review_type': review_type,
            'review_obj': review_obj
        }
        return render_template('create_review.html', title='Create Review Form', form=form, data=data, message=return_message)
    return redirect(url_for('users.login'))
