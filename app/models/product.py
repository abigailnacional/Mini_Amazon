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
    def get_specific(seller_affiliation):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
RIGHT OUTER JOIN Sells ON Product.id=Sells.product_id
WHERE seller_affiliation = :seller_affiliation AND is_available = True
ORDER BY id
''',
                                seller_affiliation=seller_affiliation)
        return [Product(*row) for row in rows] if rows is not None else None                 

    @staticmethod
    def get_all(is_available=True):
        rows = app.db.execute('''
SELECT id, name, description, category, price, is_available, creator_id, image
FROM Product
WHERE is_available = :is_available
''',
                              is_available=is_available)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_categories(is_available=True):
        rows = app.db.execute('''
SELECT DISTINCT category
FROM Product
WHERE is_available = :is_available
''',
                                is_available=is_available)
        return rows 

# method to return filtered view of venue products by category (entrées, beverages, etc.)
    @staticmethod
    def filteredCat(seller_affiliation, category):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
RIGHT OUTER JOIN Sells ON Product.id=Sells.product_id
WHERE seller_affiliation = :seller_affiliation AND is_available = True AND category = :category
ORDER BY id
''',
                              seller_affiliation=seller_affiliation,
                              category=category)
        return [Product(*row) for row in rows]  

    @staticmethod
    def filteredPrice():
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
ORDER BY price ASC
''',)
        return [Product(*row) for row in rows] 

    @staticmethod
    def filteredRating(stars):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product FULL OUTER JOIN Feedback ON Product.id = Feedback.product_id
GROUP BY id
HAVING AVG(rating) >= :stars
ORDER BY id
''',
                            stars=stars)
        return [Product(*row) for row in rows] 

    @staticmethod
    def search_filter(search):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
WHERE LOWER(name) LIKE '%' || :search || '%' OR UPPER(name) LIKE '%' || :search || '%' OR name LIKE '%' || :search || '%'
''',
                            search=search)
        return [Product(*row) for row in rows] 

    @staticmethod
    def search_id(id):
        rows = app.db.execute('''
SELECT DISTINCT id, name, description, category, price, is_available, creator_id, image
FROM Product
WHERE id = :id
''',
                            id=id)
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

    