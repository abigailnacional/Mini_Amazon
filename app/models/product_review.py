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
    def get_product_reviews(product_id):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Feedback
            WHERE product_id = :id
            ''',
            id=product_id)

        reviews = [ProductReview(*row) for row in rows]

        return reviews

    @staticmethod
    def get_user_reviews(reviewer_id):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Feedback
            WHERE reviewer_id = :id
            ''',
            id=reviewer_id)

        reviews = [ProductReview(*row) for row in rows]

        return reviews

    @staticmethod
    def get_specific_product_review_by_user(user_id, product_id):
        rows = app.db.execute(
             '''
             SELECT *
             FROM Feedback
             WHERE (reviewer_id = :user_id and product_id = :product_id)
             ''',
             user_id = user_id,
             product_id = product_id)
    
        return ProductReview(*(rows[0])) if rows is not None else None

    @staticmethod
    def check_user_review_exists(user_id, product_id):
        review = ProductReview.get_specific_product_review_by_user(user_id, product_id)
        return review != None

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
