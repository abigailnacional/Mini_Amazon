\COPY Users FROM 'data/Users.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Product FROM 'data/Product.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Cart FROM 'data/Cart.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sells FROM 'data/Sells.csv' WITH DELIMITER ',' NULL '' CSV
\COPY ProductInCart FROM 'data/ProductInCart.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Purchase FROM 'data/Purchase.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Feedback FROM 'data/Feedback.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Coupon FROM 'data/Coupon.csv' WITH DELIMITER ',' NULL '' CSV