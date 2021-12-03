from flask import current_app as app

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
    def get_reviews(id, review_type):
        if review_type == "product":
            rows = app.db.execute(
                '''
                SELECT *
                FROM Feedback
                WHERE product_id = :id
                ORDER BY upvotes DESC
                ''',
                id=id)

            reviews = [ProductReview(*row) for row in rows]

            return reviews
        else:
            rows = app.db.execute(
                '''
                SELECT *
                FROM Feedback
                WHERE seller_id = :id
                ORDER BY upvotes DESC
                ''',
                id=id)

            reviews = [ProductReview(*row) for row in rows]

            return reviews

    @staticmethod
    def get_reviews_by_user(reviewer_id):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Feedback
            WHERE reviewer_id = :id
            ORDER BY time_posted DESC
            ''',
            id=reviewer_id)

        reviews = [ProductReview(*row) for row in rows]

        return reviews

    @staticmethod
    def get_specific_review_by_user(user_id, id, review_type):
        if review_type == "product":
            rows = app.db.execute(
                '''
                SELECT *
                FROM Feedback
                WHERE (reviewer_id = :user_id and product_id = :product_id)
                ''',
                user_id=user_id,
                product_id=id)
        
            return ProductReview(*(rows[0])) if rows else []
        else:
            rows = app.db.execute(
                '''
                SELECT *
                FROM Feedback
                WHERE (reviewer_id = :user_id and seller_id = :seller_id)
                ''',
                user_id=user_id,
                seller_id=id)
        
            return ProductReview(*(rows[0])) if rows else []

    @staticmethod
    def remove_specific_review_by_user(user_id, id, review_type):
        if review_type == "product":
            app.db.execute_with_no_return(
                '''
                DELETE FROM Feedback
                WHERE (reviewer_id = :user_id and product_id = :product_id)
                ''',
                user_id=user_id,
                product_id=id)
        else:
            app.db.execute_with_no_return(
                '''
                DELETE FROM Feedback
                WHERE (reviewer_id = :user_id and seller_id = :seller_id)
                ''',
                user_id=user_id,
                seller_id=id)

    @staticmethod
    def get_summary_rating(id, review_type):
        if review_type == "product":
            rows = app.db.execute(
                '''
                SELECT COUNT(rating), AVG(rating)
                FROM Feedback
                WHERE product_id = :id
                ''',
                id=id)

            ret = (rows[0][0], "{:.1f}".format(rows[0][1]) if rows[0][0] != 0 else "No ratings yet")

            return ret
        else:
            rows = app.db.execute(
                '''
                SELECT COUNT(rating), AVG(rating)
                FROM Feedback
                WHERE seller_id = :id
                ''',
                id=id)

            ret = (rows[0][0], "{:.1f}".format(rows[0][1]) if rows[0][0] != 0 else "No ratings yet")

            return ret

    @staticmethod
    def get_product_average_rating(product_ids):
        ret = []

        rows = app.db.execute(
            """
            SELECT product_id, AVG(rating)
            FROM Feedback
            GROUP BY product_id
            """
        )

        # fast computation of average rating through sorting and dict lookups
        rows.sort(key=lambda x:x[0])
        rows_dict = {i[0]: i[1] for i in rows}
        for product_id in product_ids:
            avg = rows_dict.get(product_id)
            ret.append("{:.1f}".format(avg) if avg != None else "No ratings yet")

        return ret

    @staticmethod
    def check_user_review_exists(user_id, id, review_type):
        review = ProductReview.get_specific_review_by_user(user_id, id, review_type)

        return review != []

    @staticmethod
    def upvote_review(contents):
        # TODO: reviewer_id used to prevent one reviewer from upvoting same review more than once
        reviewer_id = contents['reviewer_id']
        product_id = contents['product_id']
        seller_id = contents['seller_id']

        app.db.execute_with_no_return(
            """
            UPDATE Feedback
            SET upvotes = upvotes + 1
            WHERE product_id = :product_id AND seller_id = :seller_id
            """,
            product_id=product_id,
            seller_id=seller_id
        )

    @staticmethod
    def update_review(review_contents):
        reviewer_id = review_contents['reviewer_id']
        rating = review_contents['rating']
        review = review_contents['review']
        product_id = review_contents['product_id']
        seller_id = review_contents['seller_id']
        time_posted = review_contents['time_posted']

        app.db.execute_with_no_return(
            """
            UPDATE Feedback
            SET rating = :rating, review = :review, time_posted = :time_posted
            WHERE reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            reviewer_id=reviewer_id,
            rating=rating,
            review=review,
            product_id=product_id,
            seller_id=seller_id,
            time_posted=time_posted
        )


    @staticmethod
    def add_review(contents):
        reviewer_id = contents['reviewer_id']
        rating = contents['rating']
        review = contents['review']
        product_id = contents['product_id']
        seller_id = contents['seller_id']
        time_posted = contents['time_posted']
        upvotes = contents['upvotes']

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
