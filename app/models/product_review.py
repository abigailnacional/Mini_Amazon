from flask import current_app as app

class ProductRating:
    def __init__(reviewer_id, rating, review, product_id, seller_id, time_posted):
        self.reviewer_id = reviewer_id
        self.rating = rating
        self.review = review
        self.product_id = product_id
        self.seller_id = seller_id
        self.time_posted = time_posted

    @staticmethod
    def get(reviewer_id):
        rows = app.db.execute(
            '''
            SELECT reviewer_id, rating, review, product_id, seller_id, time_posted
            FROM Feedback
            WHERE reviewer_id = :id
            ''',
            id = reviewer_id)

        return ProductRating(*(rows[0])) if rows is not None else None