import random
import string
import csv
import math
import datetime

import names
from random_address import real_random_address

letters = string.ascii_lowercase

base = 2000
num_total_users = 1000
num_users_with_carts = 5
num_restaurants = 6
num_sellers = 20
num_products = 5000
num_carts_per_user = 1000
num_carts_populated_per_user = 3

# sample realistic product data to show functionality of site (source: Duke Mobile Dining app)
sample_products = {1000: {'product-id': 1000, 'id': 1, 'name': 'Au Lait', 'description': 'coffee and steamed milk', 'category': 'Beverages', 'price': 3.10, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1001: {'product-id': 1001, 'id': 1, 'name': 'Mexican Coffee', 'description': 'chocalate cinnamon nutmeg and steamed milk', 'category': 'Beverages', 'price': 3.35, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'},
                    1002: {'product-id': 1002, 'id': 1, 'name': 'Caramello', 'description': 'caramell, vanilla, steamed milk, and caramel drizzle', 'category': 'Beverages', 'price': 4.65, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1003: {'product-id': 1003, 'id': 2, 'name': 'Black Bean Burger', 'description': 'spicy black bean patty with lettuce, tomato, onion, and fat free ranch on wheat roll', 'category': 'Entrées', 'price': 10.39, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1004: {'product-id': 1004, 'id': 2, 'name': 'Strawberry Banana Shake', 'description': 'real ice cream milk and strawberries, hand dipped and topped with whipped cream', 'category': 'Desserts', 'price': 5.69, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'},
                    1005: {'product-id': 1005, 'id': 2, 'name': 'Onion Rings', 'description': '10 panko battered onion rings served with a creamy jalapeño horse raddish sauce', 'category': 'Sides', 'price': 6.89, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1006: {'product-id': 1006, 'id': 3, 'name': 'Big Mac', 'description': 'two 100% pure beef patties and Big Mac sauce sandwiched between a sesame seed bun', 'category': 'Entrées', 'price': 4.99, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1007: {'product-id': 1007, 'id': 3, 'name': 'French Fries', 'description': 'world famous fries made with prenium potatoes', 'category': 'Sides', 'price': 3.19, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'},
                    1008: {'product-id': 1008, 'id': 3, 'name': 'Mango Pineapple Smoothie', 'description': 'sweet combination of fruit juices and purees such as mango and pineapple', 'category': 'Beverages', 'price': 3.89, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1009: {'product-id': 1009, 'id': 4, 'name': 'Beijing Beef', 'description': 'crispy beef, bell peppers and onions in a sweet-tangy sauce', 'category': 'Entrées', 'price': 6.40, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1010: {'product-id': 1010, 'id': 4, 'name': 'Crispy Almond Chicken', 'description': 'all-white meat chicken with out crunchy, signature puffed-rice breading that is wok-tossed with toasted almonds & freshly chopped green onions in a savory soy garlic sauce', 'category': 'Entrées', 'price': 6.40, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'},
                    1011: {'product-id': 1011, 'id': 4, 'name': 'Bottled Drink', 'description': 'description unavailable', 'category': 'Beverages', 'price': 2.10, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1012: {'product-id': 1012, 'id': 5, 'name': 'Spicy Il Forno', 'description': 'fennel sausage, spicy arrabbiata sauce, peppers & onions, rigatoni, green onions, roasted tomatoes, romano', 'category': 'Entrées', 'price': 9.35, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'},        
                    1013: {'product-id': 1013, 'id': 5, 'name': 'Garden Pesto', 'description': 'pesto sauce, fettuccine, spinach, tomatoes, mushrooms, red peppers, basil, romano', 'category': 'Entrées', 'price': 9.35, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'},
                    1014: {'product-id': 1014, 'id': 5, 'name': 'Lemon Pelligrino', 'description': 'description unavailable', 'category': 'Beverages', 'price': 3.35, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1015: {'product-id': 1015, 'id': 6, 'name': 'Arepa Bowl', 'description': 'latin bowl customized with your choice of toppings', 'category': 'Entrées', 'price': 9.35, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}, 
                    1016: {'product-id': 1016, 'id': 6, 'name': '2 Tacos', 'description': 'tacos customized with your choice of protein and toppings', 'category': 'Beverages', 'price': 9.35, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'},
                    1017: {'product-id': 1017, 'id': 6, 'name': 'Smart Water', 'description': 'description unavailable', 'category': 'Beverages', 'price': 2.00, 'is_available': 'True', 'creator_id': random.randint(base, base + num_total_users - 1), 'image': 'x'}}

print("Starting data generation on Users")

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
        # names are generated using the names Python module created by Trey Hunner
        # source: https://moonbooks.org/Articles/How-to-generate-random-names-first-and-last-names-with-python-/
        first = names.get_first_name()
        last = names.get_last_name()
        balance = random.randint(0, 1000000000)
        # addresses are generated using the random address Python tool which accurately geocodes to data collected from the Open
        # Addresses project (would need additional data for other states - beyond scope of this project)
        # source: 
        address = real_random_address()['address1']
        writer.writerow([id, email, password, first, last, balance, address])

    writer.writerow([-1, " ", " ", " ", " ", 0, " "])

print("Data generation on Users done, starting data generation on Cart")

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

            writer.writerow([cart_id, user_id, is_current, time_purchased, False, None])

            cart_id += 1

print("Data generation on Cart done, starting data generation on Product")

with open('db/data/Product.csv', 'w', newline='') as product_file:
    writer = csv.writer(product_file, delimiter=',')
    for sample in sample_products:
        writer.writerow([sample_products[sample]['product-id'], sample_products[sample]['name'], sample_products[sample]['description'], 
                        sample_products[sample]['category'], sample_products[sample]['price'], sample_products[sample]['is_available'], 
                        sample_products[sample]['creator_id'], sample_products[sample]['image']])
    for num in range(base, base + num_products):
        id = num
        name = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        description = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))
        category = random.choice(['Entrées', 'Sides', 'Desserts', 'Beverages', 'Appetizers'])
        price = random.randint(0, 1000)
        is_available = bool(random.randint(0, 1))
        creator_id = random.randint(base, base + num_total_users - 1)
        image = ''.join(random.choice(letters) for i in range(random.randint(3, 20)))

        writer.writerow([id, name, description, category, price, is_available, creator_id, image])

    writer.writerow([-1, " ", " ", "Appetizers", 0, False, -1, " "])

print("Data generation on Product done, starting data generation on Sells")

sells = set()
with open('db/data/Sells.csv', 'w', newline='') as sells_file:
    writer = csv.writer(sells_file, delimiter=',')
    for sample in sample_products:
         writer.writerow([sample_products[sample]['id'], random.randint(base, base + (num_sellers * 5)),
                        sample_products[sample]['product-id'], random.randint(0, 1000000), True])
    for num in range(base, base + (num_sellers * 5), 5):  # for first 100 users, every 5th user is a seller
        seller_id = num
        for _ in range(random.randint(1,  2000)):  # have each seller sell 1 to 2000 items for now

            product_id = random.randint(base, base + num_products - 1)
            inventory = random.randint(0, 1000000)
            seller_affiliation = random.randint(1, num_restaurants)


            if (seller_id, product_id) not in sells:
                sells.add((seller_id, product_id))
                writer.writerow([seller_affiliation, seller_id, product_id, inventory, True])

print("Data generation on Sells done, starting data generation on ProductInCart")

products_in_cart = set()
with open('db/data/ProductInCart.csv', 'w', newline='') as product_in_cart_file:
    writer = csv.writer(product_in_cart_file, delimiter=',')
    product_in_cart_id = 1000

    for user_num in range(num_users_with_carts):  # 0 - 10

        for cart_num in range(int(num_carts_per_user/2), num_carts_per_user):  # 500 - 1000

            num_items_in_cart_range = range(random.randint(10, 20))
            if cart_num > 997:
                num_items_in_cart_range = range(random.randint(50, 70))

            cart_id = user_num + cart_num + base

            for index in num_items_in_cart_range:  # number of items in the given cart
                seller_id, product_id = random.choice(list(sells))
                product_in_cart_id += 1
                quantity = random.randint(1,  1000)

                products_in_cart.add((product_in_cart_id, cart_id, product_id, seller_id))
                writer.writerow([product_in_cart_id, cart_id, product_id, seller_id, quantity])

print("Data generation on ProductInCart done, starting data generation on Purchase")

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
            final_price = random.randint(0, 1000)

            writer.writerow(
                [
                    product_in_cart_id,
                    user_id,
                    "2021-09-10 13:12:58",
                    is_fulfilled,
                    time_of_fulfillment,
                    cart_id,
                    final_price]
            )

print("Data generation on Purchase done, starting data generation on Feedback")

with open('db/data/Feedback.csv', 'w', newline='') as f, open('db/data/FeedbackUpvotes.csv', 'w', newline='') as f_up, open('db/data/FeedbackReports.csv', 'w', newline='') as f_r:
    f_writer = csv.writer(f, delimiter=',')
    f_up_writer = csv.writer(f_up, delimiter=',')
    f_r_writer = csv.writer(f_r, delimiter=',')

    product_ids = random.sample(list(range(base, base + num_products)), 2500)
    seller_ids = set([sells_tuple[0] for sells_tuple in sells]) # too little sellers so just create data on them all

    for product_id in product_ids:
        sample_reviewer_ids = random.sample(list(range(base, base + num_total_users)), random.randint(1, 10))
        for sample_reviewer_id in sample_reviewer_ids:
            rating = random.randint(1, 5)
            review = ''.join(random.choice(letters) for x in range(random.randint(3, 20)))
            seller_id = -1
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            upvotes = random.randint(0, 10)
            reports = random.randint(0, 4)

            f_writer.writerow([sample_reviewer_id, rating, review, product_id, seller_id, time, upvotes, reports])
            
            upvoter_ids = random.sample(list(range(base, base + num_total_users)), random.randint(1, 10))
            for upvoter_id in upvoter_ids:
                f_up_writer.writerow([upvoter_id, sample_reviewer_id, product_id, -1])
            reporter_ids = random.sample(list(range(base, base + num_total_users)), random.randint(1, 10))
            for reporter_id in reporter_ids:
                f_r_writer.writerow([reporter_id, sample_reviewer_id, product_id, -1])
            
    for seller_id in seller_ids:
        sample_reviewer_ids = random.sample(list(range(base, base + num_total_users)), random.randint(1, 10))
        for sample_reviewer_id in sample_reviewer_ids:
            rating = random.randint(1, 5)
            review = ''.join(random.choice(letters) for x in range(random.randint(3, 20)))
            product_id = -1
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            upvotes = random.randint(0, 10)
            reports = random.randint(0, 4)

            f_writer.writerow([sample_reviewer_id, rating, review, product_id, seller_id, time, upvotes, reports])
            
            upvoter_ids = random.sample(list(range(base, base + num_total_users)), random.randint(1, 10))
            for upvoter_id in upvoter_ids:
                f_up_writer.writerow([upvoter_id, sample_reviewer_id, -1, seller_id])
            reporter_ids = random.sample(list(range(base, base + num_total_users)), random.randint(1, 10))
            for reporter_id in reporter_ids:
                f_r_writer.writerow([reporter_id, sample_reviewer_id, -1, seller_id])

print("Data generation on Feedback done, starting data generation on Coupon")

codes = set()
with open('db/data/Coupon.csv', 'w', newline='') as coupon_file:
    writer = csv.writer(coupon_file, delimiter=',')
    sells_list = list(sells)
    for num in range(0, len(sells_list), 5):
        seller_id, product_id = sells_list[num]
        code = ''.join(random.choice(letters) for i in range(random.randint(10, 12)))
        while code in codes:
            code = ''.join(random.choice(letters) for i in range(random.randint(10, 12)))
        codes.add(code)

        expiration_date = datetime.datetime.now() + datetime.timedelta(days=7)
        percent_off = 50

        writer.writerow([code, expiration_date, product_id, seller_id, percent_off])

print("Data generation on Coupon done")