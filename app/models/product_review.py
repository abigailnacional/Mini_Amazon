from flask import current_app as app

from .product import Product

import io
import matplotlib.pyplot as plt
from scipy import stats
import base64

class ProductReview:
    def __init__(self, reviewer_id, rating, review, product_id, seller_id, time_posted, upvotes, reports):
        self.reviewer_id = reviewer_id
        self.rating = rating
        self.review = review
        self.product_id = product_id
        self.seller_id = seller_id
        self.time_posted = time_posted
        self.upvotes = upvotes
        self.reports = reports

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
            num_reviews = rows[0][0]
            avg_rating = float("{:.2f}".format(rows[0][1])) if rows[0][0] != 0 else "No ratings yet"

            if num_reviews == 0:
                return (num_reviews, avg_rating, "N/A")

            current_product_rating_rows = app.db.execute(
                '''
                SELECT rating
                FROM Feedback
                WHERE product_id = :id
                ''',
                id=id)
            current_product_rating_data = [row[0] for row in current_product_rating_rows]
            current_product_rating_data_dist = {
                '1': current_product_rating_data.count(1),
                '2': current_product_rating_data.count(2),
                '3': current_product_rating_data.count(3),
                '4': current_product_rating_data.count(4),
                '5': current_product_rating_data.count(5),
            }

            category = Product.get(id).category
            category_product_rating_rows = app.db.execute(
                '''
                SELECT id
                FROM Product
                WHERE category = :category
                ''',
                category=category
            )
            category_product_rating_data = ProductReview.get_average_rating([row[0] for row in category_product_rating_rows], "product")
            category_product_rating_data = sorted([float(data) for data in category_product_rating_data if data != 'No ratings yet'], reverse=True)
            category_percentile = stats.percentileofscore(category_product_rating_data, avg_rating)
            category_ranking = category_product_rating_data.index(avg_rating) + 1

            ## Matplotlib graph code
            rating_distribution_plot = io.BytesIO()
            _, _, rating_distribution_patches = plt.hist(current_product_rating_data, [0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
                                                         facecolor='orange', rwidth=0.5)
            plt.xticks([1, 2, 3, 4, 5])
            plt.yticks([0, max(current_product_rating_data_dist.values()) + 1])
            plt.xlabel("Rating")
            plt.ylabel("# of Reviews")
            plt.title("Product Rating Distribution")
            for rect in rating_distribution_patches:
                plt.annotate("{:.0f} %".format(100 * rect.get_height() / len(current_product_rating_data)),
                             xy=(rect.get_x()+rect.get_width()/2, rect.get_height()), xytext=(0, 5),
                             textcoords='offset points', ha='center', va='bottom')
            plt.savefig(rating_distribution_plot, format='png')
            plt.close()
            rating_distribution_plot.seek(0)
            rating_distribution_plot_url = base64.b64encode(rating_distribution_plot.getvalue())

            category_percentile_plot = io.BytesIO()
            _, _, category_percentile_patches = plt.hist(category_product_rating_data, [x / 10 for x in list(range(9, 52, 2))],
                                                         facecolor='cyan', edgecolor='black')
            plt.xticks([1, 2, 3, 4, 5])
            plt.xlabel("Average Ratings")
            plt.ylabel("Frequency")
            plt.title("Average Category Rating Distribution")
            min_dist = 1E8
            highlighted_bar_index = 0
            for i, rect in enumerate(category_percentile_patches):
                temp = abs((rect.get_x() + (rect.get_width() * (1 / 2))) - avg_rating)
                if temp < min_dist:
                    min_dist = temp
                    highlighted_bar_index = i
            highlighted_rect = category_percentile_patches[highlighted_bar_index]
            highlighted_rect.set_color('green')
            highlighted_rect.set_edgecolor('black')
            plt.annotate("{:.0f}th".format(category_percentile),
                         xy=(highlighted_rect.get_x()+highlighted_rect.get_width()/2, highlighted_rect.get_height()),
                         xytext=(0, 0), textcoords='offset points', ha='center', va='bottom', fontsize=11)
            plt.savefig(category_percentile_plot, format='png')
            plt.close()
            category_percentile_plot.seek(0)
            category_percentile_plot_url = base64.b64encode(category_percentile_plot.getvalue())

            return (num_reviews, avg_rating, f'#{category_ranking}', rating_distribution_plot_url, category_percentile_plot_url)
        else:
            rows = app.db.execute(
                '''
                SELECT COUNT(rating), AVG(rating)
                FROM Feedback
                WHERE seller_id = :id
                ''',
                id=id)

            num_reviews = rows[0][0]
            avg_rating = float("{:.2f}".format(rows[0][1])) if rows[0][0] != 0 else "No ratings yet"

            if num_reviews == 0:
                return (num_reviews, avg_rating, "N/A")

            current_seller_rating_rows = app.db.execute(
                '''
                SELECT rating
                FROM Feedback
                WHERE seller_id = :id
                ''',
                id=id)
            current_seller_rating_data = [row[0] for row in current_seller_rating_rows]
            current_seller_rating_data_dist = {
                '1': current_seller_rating_data.count(1),
                '2': current_seller_rating_data.count(2),
                '3': current_seller_rating_data.count(3),
                '4': current_seller_rating_data.count(4),
                '5': current_seller_rating_data.count(5),
            }

            seller_rating_rows = app.db.execute(
                '''
                SELECT DISTINCT seller_id
                FROM Sells
                '''
            )
            seller_rating_data = ProductReview.get_average_rating([row[0] for row in seller_rating_rows], "seller")
            seller_rating_data = sorted([float(data) for data in seller_rating_data if data != 'No ratings yet'], reverse=True)
            seller_percentile = stats.percentileofscore(seller_rating_data, avg_rating)
            seller_ranking = seller_rating_data.index(avg_rating) + 1

            ## Matplotlib graph code
            rating_distribution_plot = io.BytesIO()
            _, _, rating_distribution_patches = plt.hist(current_seller_rating_data, [0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
                                                         facecolor='orange', rwidth=0.5)
            plt.xticks([1, 2, 3, 4, 5])
            plt.yticks([0, max(current_seller_rating_data_dist.values()) + 1])
            plt.xlabel("Rating")
            plt.ylabel("# of Reviews")
            plt.title("Seller Rating Distribution")
            for rect in rating_distribution_patches:
                plt.annotate("{:.0f} %".format(100 * rect.get_height() / len(current_seller_rating_data)),
                             xy=(rect.get_x()+rect.get_width()/2, rect.get_height()), xytext=(0, 5),
                             textcoords='offset points', ha='center', va='bottom')
            plt.savefig(rating_distribution_plot, format='png')
            plt.close()
            rating_distribution_plot.seek(0)
            rating_distribution_plot_url = base64.b64encode(rating_distribution_plot.getvalue())

            overall_seller_percentile_plot = io.BytesIO()
            _, _, category_percentile_patches = plt.hist(seller_rating_data, [x / 10 for x in list(range(9, 52, 2))],
                                                         facecolor='cyan', edgecolor='black')
            plt.xticks([1, 2, 3, 4, 5])
            plt.xlabel("Average Ratings")
            plt.ylabel("Frequency")
            plt.title("Average Seller Rating Distribution")
            min_dist = 1E8
            highlighted_bar_index = 0
            for i, rect in enumerate(category_percentile_patches):
                temp = abs((rect.get_x() + (rect.get_width() * (1 / 2))) - avg_rating)
                if temp < min_dist:
                    min_dist = temp
                    highlighted_bar_index = i
            highlighted_rect = category_percentile_patches[highlighted_bar_index]
            highlighted_rect.set_color('green')
            highlighted_rect.set_edgecolor('black')
            plt.annotate("{:.0f}th".format(seller_percentile),
                         xy=(highlighted_rect.get_x()+highlighted_rect.get_width()/2, highlighted_rect.get_height()),
                         xytext=(0, 0), textcoords='offset points', ha='center', va='bottom', fontsize=11)
            plt.savefig(overall_seller_percentile_plot, format='png')
            plt.close()
            overall_seller_percentile_plot.seek(0)
            overall_seller_percentile_plot_url = base64.b64encode(overall_seller_percentile_plot.getvalue())

            return (num_reviews, avg_rating, f'#{seller_ranking}', rating_distribution_plot_url, overall_seller_percentile_plot_url)

    @staticmethod
    def get_average_rating(product_ids, type):
        ret = []
        rows = None

        if type == "product":
            rows = app.db.execute(
                """
                SELECT product_id, AVG(rating)
                FROM Feedback
                WHERE product_id != -1
                GROUP BY product_id
                """
            )
        else:
            rows = app.db.execute(
                """
                SELECT seller_id, AVG(rating)
                FROM Feedback
                WHERE seller_id != -1
                GROUP BY seller_id
                """
            )

        # fast computation of average rating through sorting and dict lookups
        rows.sort(key=lambda x:x[0])
        rows_dict = {i[0]: i[1] for i in rows}
        for product_id in product_ids:
            avg = rows_dict.get(product_id)
            ret.append("{:.2f}".format(avg) if avg != None else "No ratings yet")

        return ret

    @staticmethod
    def check_user_review_exists(user_id, id, review_type):
        review = ProductReview.get_specific_review_by_user(user_id, id, review_type)

        return review != []
    
    @staticmethod
    def check_user_can_review_seller(user_id, seller_id):
        rows = app.db.execute(
            """
            SELECT *
            From Cart
            FULL OUTER JOIN ProductInCart
            ON Cart.id=ProductInCart.cart_id
            WHERE Cart.user_id = :user_id AND ProductInCart.seller_id = :seller_id
            """,
            user_id=user_id,
            seller_id=seller_id
        )

        return rows != []

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
        reports = contents['reports']

        app.db.execute_with_no_return(
            """
            INSERT INTO Feedback(reviewer_id, rating, review, product_id, seller_id, time_posted, upvotes, reports)
                VALUES (:reviewer_id, :rating, :review, :product_id, :seller_id, :time_posted, :upvotes, :reports)
            """,
            reviewer_id=reviewer_id,
            rating=rating,
            review=review,
            product_id=product_id,
            seller_id=seller_id,
            time_posted=time_posted,
            upvotes=upvotes,
            reports=reports
        )

    @staticmethod
    def check_upvote_exists(upvoter_id, reviewer_id, product_id, seller_id):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Feedback_Upvotes
            WHERE upvoter_id = :upvoter_id AND reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
            ''',
            upvoter_id=upvoter_id,
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id)
    
        return rows != []

    @staticmethod
    def upvote_review(upvoter_id, reviewer_id, product_id, seller_id):
        app.db.execute_with_no_return(
            """
            UPDATE Feedback
            SET upvotes = upvotes + 1
            WHERE reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id
        )

        app.db.execute_with_no_return(
            """
            INSERT INTO Feedback_Upvotes(upvoter_id, reviewer_id, product_id, seller_id)
                VALUES(:upvoter_id, :reviewer_id, :product_id, :seller_id)
            """,
            upvoter_id=upvoter_id,
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id
        )

    @staticmethod
    def remove_upvote(upvoter_id, reviewer_id, product_id, seller_id):
        app.db.execute_with_no_return(
            """
            UPDATE Feedback
            SET upvotes = upvotes - 1
            WHERE reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id
        )

        app.db.execute_with_no_return(
            """
            DELETE FROM Feedback_Upvotes
            WHERE upvoter_id = :upvoter_id AND reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            upvoter_id=upvoter_id,
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id
        )

    @staticmethod
    def check_report_exists(reporter_id, reviewer_id, product_id, seller_id):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Feedback_Reports
            WHERE reporter_id = :reporter_id AND reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
            ''',
            reporter_id=reporter_id,
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id)
    
        return rows != []

    @staticmethod
    def get_user_review_reports(user_id):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Feedback_Reports
            WHERE reporter_id = :reporter_id
            ''',
            reporter_id=user_id)

        return rows

    @staticmethod
    def report_review(reporter_id, reviewer_id, product_id, seller_id):
        app.db.execute_with_no_return(
            """
            UPDATE Feedback
            SET reports = reports + 1
            WHERE reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id
        )

        app.db.execute_with_no_return(
            """
            INSERT INTO Feedback_Reports(reporter_id, reviewer_id, product_id, seller_id)
                VALUES(:reporter_id, :reviewer_id, :product_id, :seller_id)
            """,
            reporter_id=reporter_id,
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id
        )

        rows = app.db.execute(
            '''
            SELECT reports
            FROM Feedback
            WHERE reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
            ''',
            reviewer_id=reviewer_id,
            product_id=product_id,
            seller_id=seller_id)

        if rows[0][0] >= 5:
            # The system automatically deletes any reviews that have 5 reports
            app.db.execute_with_no_return(
                """
                DELETE FROM Feedback
                WHERE reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
                """,
                reviewer_id=reviewer_id,
                product_id=product_id,
                seller_id=seller_id
            )

            # Getting rid of any remaining data from related tables
            app.db.execute_with_no_return(
                """
                DELETE FROM Feedback_Upvotes
                WHERE reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
                """,
                reviewer_id=reviewer_id,
                product_id=product_id,
                seller_id=seller_id
            )
            app.db.execute_with_no_return(
                """
                DELETE FROM Feedback_Reports
                WHERE reviewer_id = :reviewer_id AND product_id = :product_id AND seller_id = :seller_id
                """,
                reviewer_id=reviewer_id,
                product_id=product_id,
                seller_id=seller_id
            )