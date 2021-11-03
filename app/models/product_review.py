from flask import current_app as app

class ProductReview:
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

        return ProductReview(*(rows[0])) if rows is not None else None
    
    # TODO: not sure if this belongs here, maybe it's better belonged in Product file?
    @staticmethod
    def check_user_review_exists(user_id):
        return False

    @staticmethod
    def add_review(review_contents): #review_contents is dictionary
        reviewer_id = review_contents['reviewer_id']
        rating = review_contents['rating']
        review = review_contents['review']
        product_id = review_contents['product_id']
        seller_id = review_contents['seller_id']
        time_posted = review_contents['time_posted']

        app.db.execute_with_no_return(
            """
            INSERT INTO Feedback(reviewer_id, rating, review, product_id, seller_id, time_posted)
                VALUES (:reviewer_id, :rating, :review, :product_id, :seller_id, :time_posted)
            """,
            reviewer_id=reviewer_id,
            rating=rating,
            review=review,
            product_id=product_id,
            seller_id=seller_id,
            time_posted=time_posted
        )