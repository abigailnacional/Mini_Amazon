from flask import current_app as app

class ProductReview:
    def __init__(self, reviewer_id, rating, review, product_id, seller_id, time_posted):
        self.reviewer_id = reviewer_id
        self.rating = rating
        self.review = review
        self.product_id = product_id
        self.seller_id = seller_id
        self.time_posted = time_posted

    @staticmethod
    def get_user_reviews(reviewer_id):
        rows = app.db.execute(
            '''
            SELECT reviewer_id, rating, review, product_id, seller_id, time_posted
            FROM Feedback
            WHERE reviewer_id = :id
            ''',
            id = reviewer_id)

        pr_r = [ProductReview(*row) for row in rows]

        return pr_r

    @staticmethod
    def check_user_review_exists(user_id, product_id):
        rows = app.db.execute(
             '''
             SELECT *
             FROM Feedback
             WHERE (reviewer_id = :user_id and product_id = :product_id)
             ''',
             user_id = user_id,
             product_id = product_id)
        return len(rows) != 0

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
