-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Users (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    balance INT DEFAULT 0,
    address VARCHAR(255) UNIQUE,
    CHECK (balance >= 0)
);

CREATE TABLE Product (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255), /* changed from not null */
    category VARCHAR(255) NOT NULL,
    price DECIMAL NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    link VARCHAR(255) NOT NULL,
    creator_id INT NOT NULL,
    image VARCHAR(255) NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES Users(id)
    /*CHECK (category IN ('Food', 'Beverage', 'Antique', 'Painting'))
    */
);

CREATE TABLE Sells (
   seller_id INT NOT NULL,
   product_id INT NOT NULL,
   inventory INT NOT NULL,
   FOREIGN KEY (seller_id) REFERENCES Users(id),
   FOREIGN KEY (product_id) REFERENCES Product(id),
   PRIMARY KEY (seller_id, product_id)
);

CREATE TABLE Cart (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id INT NOT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    time_purchased timestamp without time zone DEFAULT NULL,
    is_fulfilled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE ProductInCart (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES Cart(id),
    FOREIGN KEY (seller_id, product_id) REFERENCES Sells(seller_id, product_id)
);

CREATE TABLE Purchase (
    product_in_cart_id INT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    is_fulfilled BOOLEAN DEFAULT FALSE,
    time_of_fulfillment timestamp without time zone DEFAULT NULL,
    cart_id INT NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES Cart(id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (product_in_cart_id) REFERENCES ProductInCart(id)
);

CREATE TABLE Feedback (
   reviewer_id INT NOT NULL PRIMARY KEY,
   rating INT NOT NULL,  -- this should be 1 - 5
   review VARCHAR(255) NOT NULL,
   product_id INT CHECK(product_id IS NOT NULL OR seller_id IS NOT NULL),
   seller_id INT CHECK(seller_id IS NOT NULL OR product_id IS NOT NULL),
   time_posted timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
   FOREIGN KEY (reviewer_id) REFERENCES Users(id),
   FOREIGN KEY (seller_id) REFERENCES Users(id),
   FOREIGN KEY (product_id) REFERENCES Product(id)
);
