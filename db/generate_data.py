import random
import string
import csv
import math

letters = string.ascii_lowercase

base = 1000
num_total_users = 1000
num_users_with_carts = 5
num_resturants = 6
num_sellers = 20
num_products = 5000
num_reviews = 1000
num_carts_per_user = 1000
num_carts_populated_per_user = 3

# TODO: create modules for each csv so we don't have to re-create all the data every time

with open('db/data/Users.csv', 'w', newline='') as users_file:
    writer = csv.writer(users_file, delimiter=',')
    for num in range(base, base + num_total_users):
        if num == base:
            email = "admin@gmail.com"
            password = "123"
            balance = 1000000000
        else:
            email = ''.join(random.choice(letters) for i in range(random.randint(5, 10))) + "@gmail.com"
            password = ''.join(random.choice(letters) for i in range(random.randint(8, 16)))

        id = num
        first = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        last = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        balance = random.randint(0, 1000000000)
        address = ''.join(random.choice(letters) for i in range(random.randint(20, 40)))

        writer.writerow([id, email, password, first, last, balance, address])

purchased_cart_ids = []
with open('db/data/Cart.csv', 'w', newline='') as cart_file:
    writer = csv.writer(cart_file, delimiter=',')

    cart_id = base
    for user_id in range(base, base + num_users_with_carts):
        for num_cart in range(num_carts_per_user):
            is_current = num_cart == num_carts_per_user - 1
            time_purchased = None
            if not is_current:
                time_purchased = "2021-09-10 13:12:58"
                purchased_cart_ids.append(cart_id)

            writer.writerow([cart_id, user_id, is_current, time_purchased, False])

            cart_id += 1


with open('db/data/Product.csv', 'w', newline='') as product_file:
    writer = csv.writer(product_file, delimiter=',')
    for num in range(base, base + num_products):
        id = num
        name = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        description = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        category = random.choice(['Entrées', 'Sides', 'Desserts', 'Beverages', 'Appetizers'])
        price = random.randint(0, 1000)
        is_available = bool(random.randint(0, 1))
        link = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        creator_id = random.randint(base, base + num_total_users - 1)
        image = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))

        writer.writerow([id, name, description, category, price, is_available, link, creator_id, image])


sells = set()
with open('db/data/Sells.csv', 'w', newline='') as sells_file:
    writer = csv.writer(sells_file, delimiter=',')
    for num in range(base, base + (num_sellers * 5), 5):  # for first 100 users, every 5th user is a seller
        seller_id = num
        for _ in range(random.randint(1,  2000)):  # have each seller sell 1 to 2000 items for now

            product_id = random.randint(base, base + num_products - 1)
            inventory = random.randint(0, 1000000)
            seller_affiliation = random.randint(1, num_resturants)

            if (seller_id, product_id) not in sells:
                sells.add((seller_id, product_id))
                writer.writerow([seller_affiliation, seller_id, product_id, inventory])

products_in_cart = set()
with open('db/data/ProductInCart.csv', 'w', newline='') as product_in_cart_file:
    writer = csv.writer(product_in_cart_file, delimiter=',')
    product_in_cart_id = 1000

    for user_num in range(num_users_with_carts):  # 0 - 10

        for cart_num in range(int(num_carts_per_user/2), num_carts_per_user):  # 500 - 1000

            num_items_in_cart_range = range(random.randint(10, 20))
            if cart_num > 997:
                num_items_in_cart_range = range(random.randint(100, 200))

            cart_id = user_num + cart_num + base

            for index in num_items_in_cart_range:  # number of items in the given cart
                seller_id, product_id = random.choice(list(sells))
                product_in_cart_id += 1
                quantity = random.randint(1,  1000)

                products_in_cart.add((product_in_cart_id, cart_id, product_id, seller_id))
                writer.writerow([product_in_cart_id, cart_id, product_id, seller_id, quantity])

with open('db/data/Purchase.csv', 'w', newline='') as purchase_file:
    writer = csv.writer(purchase_file, delimiter=',')

    for product_in_cart in products_in_cart:

        product_in_cart_id, cart_id, product_id, seller_id = product_in_cart

        if cart_id in purchased_cart_ids:
            user_id = math.floor((cart_id-base)/5) + base
            is_fulfilled = bool(random.randint(0, 1))
            time_of_fulfillment = None
            if is_fulfilled:
                time_of_fulfillment = "2021-09-10 13:12:58"

            writer.writerow([product_in_cart_id, user_id, "2021-09-10 13:12:58", is_fulfilled, time_of_fulfillment, cart_id])

with open('db/data/Feedback.csv', 'w', newline='') as feedback_file:
    writer = csv.writer(feedback_file, delimiter=',')

    reviewer_ids = random.sample(list(range(base, base + num_total_users)), num_reviews)
    product_ids = random.sample(list(range(base, base + num_products)), num_reviews)

    for i in range(num_reviews):
        reviewer_id = reviewer_ids[i]
        product_id = product_ids[i]
        rating = random.randint(1, 5)
        upvotes = random.randint(0, 10)
        review = ''.join(random.choice(letters) for x in range(random.randint(3, 20)))

        writer.writerow([reviewer_id, rating, review, product_id, None, "2021-11-01 18:54:37", upvotes])
