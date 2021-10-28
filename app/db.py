from sqlalchemy import create_engine, text


class DB:
    """Hosts all functions for querying the database."""
    def __init__(self, app):
        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

        # TODO find better home for this code
        self.execute_with_no_return(
            """
            PREPARE insert_purchase AS
            INSERT INTO Purchase(product_in_cart_id, user_id, cart_id)
                VALUES ($1, $2, $3)
            """
        )

    def connect(self):
        return self.engine.connect()

    def execute(self, sqlstr, **kwargs):
        """Execute sqlstr and return a list of result tuples.  sqlstr will be
        wrapped automatically in a
        sqlalchemy.sql.expression.TextClause.  You can use :param
        inside sqlstr and supply its value as a kwarg.  See
        https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.execute
        https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.text
        https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.CursorResult
        for additional details.  See models/*.py for examples of
        calling this function."""
        with self.engine.connect() as conn:
            return list(conn.execute(text(sqlstr), kwargs).fetchall())


    # the use of .fetchall() causes the execute method to error for SQL that does not return rows (i.e. UPDATE)
    def execute_with_no_return(self, sqlstr, **kwargs):
        with self.engine.connect() as conn:
            return conn.execute(text(sqlstr), kwargs)
