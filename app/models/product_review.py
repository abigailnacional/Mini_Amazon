from flask import current_app as app

import time

class ProductReview:
    def __init__(self, reviewer_id, rating, review, product_id, seller_id, time_posted, upvotes):
        self.reviewer_id = reviewer_id
        self.rating = rating
        self.review = review
        self.product_id = product_id
        self.seller_id = seller_id
        self.time_posted = time_posted
        self.upvotes = upvotes

    @staticmethod
    def get_product_reviews(product_id):
        # automatically ordered by upvotes
        rows = app.db.execute(
            '''
            SELECT *
            FROM Feedback
            WHERE product_id = :id
            ORDER BY upvotes DESC
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
            user_id=user_id,
            product_id=product_id)
    
        return ProductReview(*(rows[0])) if rows else []

    @staticmethod
    def get_product_average_rating(product_ids):
        ret = []
        # TODO: very inefficient, think of another way to do this
        for product_id in product_ids:
            rows = app.db.execute(
                '''
                SELECT AVG(rating)
                FROM Feedback
                WHERE product_id = :id
                ''',
                id=product_id)

            if rows[0][0] == None:
                ret.append("No ratings yet")
            else:
                ret.append("{:.1f}".format(rows[0][0]))
        
        return ret

    @staticmethod
    def check_user_review_exists(user_id, product_id):
        review = ProductReview.get_specific_product_review_by_user(user_id, product_id)
        return review != []

    @staticmethod
    def upvote_review(contents):
        reviewer_id = contents['reviewer_id']
        product_id = contents['product_id']

        app.db.execute_with_no_return(
            """
            UPDATE Feedback
            SET upvotes = upvotes + 1
            WHERE reviewer_id = :reviewer_id AND product_id = :product_id 
            """,
            reviewer_id=reviewer_id,
            product_id=product_id
        )

    # TODO: refactor from add_review()
    @staticmethod
    def update_review(review_contents):
        reviewer_id = review_contents['reviewer_id']
        rating = review_contents['rating']
        review = review_contents['review']
        product_id = review_contents['product_id']
        time_posted = review_contents['time_posted']

        app.db.execute_with_no_return(
            """
            UPDATE Feedback
            SET rating = :rating, review = :review, time_posted = :time_posted
            WHERE reviewer_id = :reviewer_id AND product_id = :product_id 
            """,
            reviewer_id=reviewer_id,
            rating=rating,
            review=review,
            product_id=product_id,
            time_posted=time_posted
        )


    @staticmethod
    def add_review(review_contents):
        reviewer_id = review_contents['reviewer_id']
        rating = review_contents['rating']
        review = review_contents['review']
        product_id = review_contents['product_id']
        seller_id = review_contents['seller_id']
        time_posted = review_contents['time_posted']
        upvotes = review_contents['upvotes']

        app.db.execute_with_no_return(
            """
            INSERT INTO Feedback(reviewer_id, rating, review, product_id, seller_id, time_posted, upvotes)
                VALUES (:reviewer_id, :rating, :review, :product_id, :seller_id, :time_posted, :upvotes)
            """,
            reviewer_id=reviewer_id,
            rating=rating,
            review=review,
            product_id=product_id,
            seller_id=seller_id,
            time_posted=time_posted,
            upvotes=upvotes
        )
