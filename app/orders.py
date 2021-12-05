from app.models.purchase import Purchase
from flask_login import current_user
from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from flask_babel import _, lazy_gettext as _l
from datetime import datetime, timedelta

from .models.cart import Cart

from flask import Blueprint

bp = Blueprint('order', __name__)


@bp.route('/view_orders')
def view_orders():
    """
    This method fetches all purchased carts for the current user
    """

    if current_user.is_authenticated:
        page_num = int(request.args.get('page', default=1))

        # need all past carts
        purchased_carts = Cart.get_purchased_carts(current_user.id, page_num)

        return render_template(
            'orders.html',
            purchased_carts=purchased_carts,
            page_num=page_num
        )
    return redirect(url_for('users.login'))

"""
This form allows the user to select filters for the purchase history.
For "Fulfillment Status", users can opt to see only fulfilled carts,
only unfulfilled carts, or all carts regardless of fulfillment.
For the second type of filter, users can view the most recent orders
by selecting if they want to view orders that were purchased within 1
day ago, or 2/5/10 days ago.
"""
class OrderFiltersForm(FlaskForm):
    fulfill = SelectField(_l('Fulfillment Status'),
        choices = [(0, 'All'), (1, 'Fulfilled'), (2, 'Unfulfilled')],
        validators=[DataRequired()]
    )
    time_period = SelectField(_l('Show orders purchased within:'),
        choices = [(0, 'All'), (1, '1 day ago'), (2, '2 days ago'), (5, '5 days ago'), (10, '10 days ago')],
        validators=[DataRequired()]
    )
    submit = SubmitField(_l('Apply Filter(s)'))


"""
This method saves the filter parameters that the user selects for the purchase history.
"""
@bp.route('/filters_for_orders', methods=['GET', 'POST'])
def filters_for_orders():
    if current_user.is_authenticated:
        form = OrderFiltersForm()
        if form.validate_on_submit():
            fulfill = form.fulfill.data
            time_period = form.time_period.data
            return redirect(url_for('order.filtered_orders', 
            fulfill=fulfill, time_period=time_period, page = 1))
        return render_template('order_filters.html', form=form)
    return redirect(url_for('users.login'))

"""
This method filters the purchase history and displays it to the user.
"""
@bp.route('/filtered_orders/')
def filtered_orders():
    if current_user.is_authenticated:
        page_num = int(request.args.get('page'))
        fulfill = request.args.get('fulfill')
        time_period = request.args.get('time_period')

        # need all past carts
        purchased_carts = Cart.get_purchased_carts(current_user.id, page_num)

        #Filtering for fulfilled carts
        if fulfill == '1':
            fulfilled_carts = []
            for some_cart in purchased_carts:
                if some_cart.is_fulfilled:
                    fulfilled_carts.append(some_cart)
            purchased_carts = fulfilled_carts
        #Filtering for unfulfilled carts
        elif fulfill == '2':
            unfulfilled_carts = []
            for some_cart in purchased_carts:
                if not some_cart.is_fulfilled:
                    unfulfilled_carts.append(some_cart)
            purchased_carts = unfulfilled_carts
        elif fulfill == '0':
            purchased_carts = purchased_carts
        
        if time_period != '0':
            recent_carts = []
            for some_cart in purchased_carts:
                #If the time that has elapsed between when the cart was purchased
                #and now is less than the time given, add the cart
                time_now = datetime.now()
                elapsed_time = time_now - some_cart.time_purchased
                recent_time = timedelta(days = int(time_period))
                if elapsed_time <= recent_time:
                    recent_carts.append(some_cart)
            purchased_carts = recent_carts
        elif time_period == '0':
            purchased_carts = purchased_carts
            
        return render_template(
            'filtered_orders.html',
            purchased_carts=purchased_carts,
            page_num=page_num,
            fulfill=fulfill,
            time_period=time_period
        )
    return redirect(url_for('users.login'))

@bp.route('/incoming_orders', methods=['GET'])
def incoming_orders():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    orders = Purchase.get_seller_incoming_orders(current_user.id)

    return render_template(
            'incoming_orders.html',
            incoming_orders=orders)

@bp.route('/fulfilled_orders', methods=['GET'])
def fulfilled_orders():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    orders = Purchase.get_seller_fulfilled_orders(current_user.id)

    return render_template(
            'fulfilled_orders.html',
            fulfilled_orders=orders)


@bp.route('/order/fulfill/<id>/<cart_id>', methods=['POST'])
def fulfill(id, cart_id):
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    
    Purchase.mark_as_fulfilled(id, cart_id)

    return redirect(url_for('order.incoming_orders'))
