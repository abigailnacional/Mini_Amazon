import random
import string
import csv
import math
import datetime

letters = string.ascii_lowercase

base = 1000
num_users = 100
num_products = 1000
num_carts = 500  # each user has one present cart, 4 past carts

with open('db/data/Users.csv', 'w', newline='') as users_file:
    writer = csv.writer(users_file, delimiter=',')
    for num in range(base, base + num_users):
        if num == base:
            email = "admin@gmail.com"
            password = "123"
        else:
            email = ''.join(random.choice(letters) for i in range(random.randint(5, 10))) + "@gmail.com"
            password = ''.join(random.choice(letters) for i in range(random.randint(8, 16)))

        id = num
        first = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        last = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        balance = random.randint(0, 1000000000)
        address = ''.join(random.choice(letters) for i in range(random.randint(20, 40)))


        writer.writerow([id, email, password, first, last, balance, address])


with open('db/data/Cart.csv', 'w', newline='') as cart_file:
    writer = csv.writer(cart_file, delimiter=',')
    for cart_id in range(base, base + num_carts):
        user_id = math.floor((cart_id-base)/5) + base  # 5 carts for each user
        is_current = bool(cart_id % 5 == 4)

        writer.writerow([cart_id, user_id, is_current])


with open('db/data/Product.csv', 'w', newline='') as product_file:
    writer = csv.writer(product_file, delimiter=',')
    for num in range(base, base + num_products):
        id = num
        name = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        description = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        category = random.choice(['Food', 'Beverage', 'Antique', 'Painting'])
        price = random.randint(0, 100000)
        is_available = bool(random.randint(0, 1))
        link = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        creator_id = random.randint(base, base + num_users-1)
        image = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))

        writer.writerow([id, name, description, category, price, is_available, link, creator_id, image])


sells = set()
with open('db/data/Sells.csv', 'w', newline='') as sells_file:
    writer = csv.writer(sells_file, delimiter=',')
    for num in range(base, base + num_users, 5):
        seller_id = num
        for _ in range(random.randint(1,  200)):  # have each seller sell 1 to 200 items for now

            product_id = random.randint(base, base + num_products - 1)
            inventory = random.randint(0, 1000000)

            if (seller_id, product_id) not in sells:
                sells.add((seller_id, product_id))
                writer.writerow([seller_id, product_id, inventory])

products_in_cart = []
with open('db/data/ProductInCart.csv', 'w', newline='') as product_in_cart_file:
    writer = csv.writer(product_in_cart_file, delimiter=',')
    product_in_cart_id = 0

    for num in range(base, base + num_carts):

        cart_id = num

        for index in range(random.randint(100, 200)):  # number of items in the given cart
            seller_id, product_id = random.choice(list(sells))
            product_in_cart_id += 1
            quantity = random.randint(1,  100000)

            products_in_cart.append((product_in_cart_id, cart_id, product_id, seller_id))
            writer.writerow([product_in_cart_id, cart_id, product_id, seller_id, quantity])

with open('db/data/Purchase.csv', 'w', newline='') as purchase_file:
    writer = csv.writer(purchase_file, delimiter=',')

    for product_in_cart in products_in_cart:

        product_in_cart_id, cart_id, product_id, seller_id = product_in_cart

        if cart_id % 5 != 4:  # if cart id not divisible by 5, has been purchased
            user_id = math.floor((cart_id-base)/5) + base
            is_fulfilled = bool(random.randint(0, 1))
            time_of_fulfillment = None
            if is_fulfilled:
                time_of_fulfillment = "2021-09-10 13:12:58"

            writer.writerow([product_in_cart_id, user_id, "2021-09-10 13:12:58", is_fulfilled, time_of_fulfillment, cart_id])





        # app.db.execute_with_no_return(
        #     """
        #     EXECUTE create_user(:email, :password, :first, :last, :balance, :address)
        #     """,
        #     email=email,
        #     password=password,
        #     first=first,
        #     last=last,
        #     balance=balance,
        #     address=address
        # )


        # app.db.execute_with_no_return(
        #     """
        #     PREPARE create_user AS
        #     INSERT INTO User(email, password, first, last, balance, address)
        #     VALUES ($1, $2, $3, $4, $5, $6)
        #     """
        # )
