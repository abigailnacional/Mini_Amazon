from flask import current_app as app


class Product:
    def __init__(
            self,
            id,
            name,
            description,
            category,
            price,
            is_available,
            link,
            creator_id,
            image
    ):
        self.id = id
        self.name = name
        self.price = price
        self.is_available = is_available
        self.description = description
        self.category = description
        self.link = link
        self.creator_id = creator_id
        self.image = image

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, description, category, price, is_available, link, creator_id, image
FROM Product
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(is_available=True):
        rows = app.db.execute('''
SELECT id, name, description, category, price, is_available, link, creator_id, image
FROM Product
WHERE is_available = :is_available
''',
                              is_available=is_available)
        return [Product(*row) for row in rows]
