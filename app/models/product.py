from flask import current_app as app
import random

class Product:
    def __init__(
            self,
            id,
            name,
            description,
            category,
            price,
            is_available,
            creator_id,
            image
    ):
        self.id = id
        self.name = name
        self.price = price
        self.is_available = is_available
        self.description = description
        self.category = category
        self.creator_id = creator_id
        self.image = image

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, description, category, price, is_available, creator_id, image
FROM Product
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

# method to return products served by a specific on-campus resturant venue
    @staticmethod
    def get_specific(seller_affiliation, page_num):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
RIGHT OUTER JOIN Sells ON Product.id=Sells.product_id
WHERE seller_affiliation = :seller_affiliation AND is_available = True
ORDER BY id
LIMIT 20
OFFSET ((:page_num - 1) * 20)
''',
                                seller_affiliation=seller_affiliation,
                                page_num=page_num)
        return [Product(*row) for row in rows] if rows is not None else None                 

# method to return all available products
    @staticmethod
    def get_all(is_available=True):
        rows = app.db.execute('''
SELECT id, name, description, category, price, is_available, creator_id, image
FROM Product
RIGHT OUTER JOIN Sells ON Product.id=Sells.product_id
WHERE is_available = :is_available
''',
                              is_available=is_available)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_categories(is_available=True):
        rows = app.db.execute('''
SELECT DISTINCT category
FROM Product
RIGHT OUTER JOIN Sells ON Product.id=Sells.product_id
WHERE is_available = :is_available
''',
                                is_available=is_available)
        return rows 

# method to return filtered view of venue products by category (entrées, beverages, etc.)
    @staticmethod
    def filteredCat(seller_affiliation, category, page_num):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
RIGHT OUTER JOIN Sells ON Product.id=Sells.product_id
WHERE seller_affiliation = :seller_affiliation AND is_available = True AND category = :category
ORDER BY id
LIMIT 20
OFFSET ((:page_num - 1) * 20)
''',
                              seller_affiliation=seller_affiliation,
                              category=category,
                              page_num=page_num)
        return [Product(*row) for row in rows]  

# method to filter by price (ordered from lowest to highest)
    @staticmethod
    def filteredPrice(seller_affiliation, page_num):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product RIGHT OUTER JOIN Sells ON Product.id=Sells.product_id
WHERE seller_affiliation = :seller_affiliation AND is_available = True
ORDER BY price ASC
LIMIT 20
OFFSET ((:page_num - 1) * 20)
''',
                                seller_affiliation=seller_affiliation,
                                page_num=page_num)
        return [Product(*row) for row in rows] 

# method to return filtered view of venue products by their current average rating
    @staticmethod
    def filteredRating(stars, page_num):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product FULL OUTER JOIN Feedback ON Product.id = Feedback.product_id
GROUP BY id
HAVING AVG(rating) >= :stars
ORDER BY id
LIMIT 20
OFFSET ((:page_num - 1) * 20)
''',
                            stars=stars,
                            page_num=page_num)
        return [Product(*row) for row in rows] 

# method to return filtered view of venue products by search query
    @staticmethod
    def search_filter(search, page_num):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
WHERE LOWER(name) LIKE '%' || :search || '%' OR UPPER(name) LIKE '%' || :search || '%' OR name LIKE '%' || :search || '%'
LIMIT 20
OFFSET ((:page_num - 1) * 20)
''',
                            search=search,
                            page_num=page_num)
        return [Product(*row) for row in rows] 

    @staticmethod
    def search_id(id, page_num):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
RIGHT OUTER JOIN Sells ON Product.id=Sells.product_id
WHERE id = :id
AND is_available = true
LIMIT 20
OFFSET ((:page_num - 1) * 20)
''',
                            id=id,
                            page_num=page_num)
        return [Product(*row) for row in rows] 

    @staticmethod
    def add_product(name, description, price, category, image, current_user):
        rows = app.db.execute('''
INSERT INTO Product (name, description, category, price, is_available, image, creator_id)
VALUES (:name, :description, :category, :price, :is_available, :image, :creator_id)
RETURNING id
    ''',
        name=name,
        description=description,
        category=category,
        price=price,
        image=image,
        creator_id=current_user.id,
        is_available=True
        )
        id = rows[0][0]
        return id

    @staticmethod
    def update_name(product_id, name):
        rows = app.db.execute_with_no_return('''
UPDATE Product
SET name = :name
WHERE id = :product_id
        ''',
            name=name,
            product_id=product_id)

    @staticmethod
    def update_description(product_id, description):
        rows = app.db.execute_with_no_return('''
UPDATE Product
SET description = :description
WHERE id = :product_id
        ''',
            description=description,
            product_id=product_id)

    @staticmethod
    def update_price(product_id, price):
        rows = app.db.execute_with_no_return('''
UPDATE Product
SET price = :price
WHERE id = :product_id
        ''',
            price=price,
            product_id=product_id)

    @staticmethod
    def update_category(product_id, category):
        rows = app.db.execute_with_no_return('''
UPDATE Product
SET category = :category
WHERE id = :product_id
        ''',
            category=category,
            product_id=product_id)

    @staticmethod
    def update_availability(product_id, available):
        rows = app.db.execute_with_no_return('''
UPDATE Product
SET is_available = :available
WHERE id = :product_id
        ''',
            available=available,
            product_id=product_id)
        
        