from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Restaurant, MenuItem, User, Review, Coupon


COUPONS_DATA = [
    {
        "code": "ZOMATO50",
        "description": "50% OFF up to ₹100 on orders above ₹199",
        "discount_type": "PERCENT",
        "discount_value": 50.00,
        "min_order_amount": 199.00,
        "max_discount": 100.00,
        "is_active": True,
    },
    {
        "code": "WELCOME100",
        "description": "Flat ₹100 OFF on your meal for orders above ₹299",
        "discount_type": "FLAT",
        "discount_value": 100.00,
        "min_order_amount": 299.00,
        "max_discount": None,
        "is_active": True,
    },
    {
        "code": "HUNGRY20",
        "description": "20% OFF up to ₹150 on food orders above ₹250",
        "discount_type": "PERCENT",
        "discount_value": 20.00,
        "min_order_amount": 250.00,
        "max_discount": 150.00,
        "is_active": True,
    },
    {
        "code": "FEAST30",
        "description": "30% OFF up to ₹200 on meals above ₹499",
        "discount_type": "PERCENT",
        "discount_value": 30.00,
        "min_order_amount": 499.00,
        "max_discount": 200.00,
        "is_active": True,
    },
]


RESTAURANTS_DATA = [
    {
        "name": "Spice Villa",
        "description": "North Indian curries, tandoori breads, and Mughlai specialties.",
        "cuisine": "North Indian",
        "address": "12 MG Road, South Tukoganj",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&auto=format&fit=crop&q=80",
        "rating": 4.3,
        "avg_cost_for_two": 600,
        "delivery_time": 35,
        "is_pure_veg": False,
        "is_open": True,
        "order_count": 890,
        "menu_items": [
            {
                "title": "Butter Chicken",
                "price": 280.0,
                "description": "Tender chicken cooked in rich butter-tomato gravy.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=600&auto=format&fit=crop&q=80",
                "is_veg": False,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Paneer Tikka",
                "price": 220.0,
                "description": "Marinated paneer grilled in tandoor with bell peppers and onions.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Dal Makhani",
                "price": 190.0,
                "description": "Slow cooked black lentils simmered with cream and butter.",
                "category": "Main Course",
                "is_veg": True,
                "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80",
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Garlic Butter Naan",
                "price": 55.0,
                "description": "Freshly baked flatbread topped with minced garlic and melted butter.",
                "category": "Main Course",
                "is_veg": True,
                "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=600&auto=format&fit=crop&q=80",
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Gulab Jamun with Ice Cream",
                "price": 95.0,
                "description": "Warm sugar-soaked gulab jamun served alongside cold vanilla ice cream.",
                "category": "Desserts",
                "is_veg": True,
                "image_url": "https://images.unsplash.com/photo-1667789397941-657d478cf8e9?w=600&auto=format&fit=crop&q=80",
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Sweet Mango Lassi",
                "price": 80.0,
                "description": "Rich yogurt cooler blended with fresh mango pulp.",
                "category": "Beverages",
                "is_veg": True,
                "image_url": "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=600&auto=format&fit=crop&q=80",
                "is_bestseller": False,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Dragon Wok",
        "description": "Indo-Chinese street food noodles, fried rice, and gravies.",
        "cuisine": "Chinese",
        "address": "Vijay Nagar, Scheme 54",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&auto=format&fit=crop&q=80",
        "rating": 4.1,
        "avg_cost_for_two": 450,
        "delivery_time": 30,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 650,
        "menu_items": [
            {
                "title": "Veg Hakka Noodles",
                "price": 180.0,
                "description": "Wok-tossed noodles with shredded vegetables and savory soy seasoning.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Chilli Paneer Dry",
                "price": 210.0,
                "description": "Crisp paneer cubes tossed with capsicum, onion, and spicy garlic chili sauce.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Veg Manchurian Gravy",
                "price": 190.0,
                "description": "Vegetable dumplings simmered in rich ginger-garlic and dark soy gravy.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1525755662778-989d0524087e?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Crispy Spring Rolls (4 Pcs)",
                "price": 150.0,
                "description": "Crispy fried rolls stuffed with seasoned shredded cabbage, carrots, and glass noodles.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Honey Chilli Noodles with Ice Cream",
                "price": 130.0,
                "description": "Golden fried crispy noodles coated in honey glaze with vanilla ice cream.",
                "category": "Desserts",
                "image_url": "https://images.unsplash.com/photo-1505394033641-40c6ad1178d7?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Iced Lemon Green Tea",
                "price": 75.0,
                "description": "Brewed green tea chilled with lemon and mint.",
                "category": "Beverages",
                "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Guru Kripa Pure Veg",
        "description": "Wholesome vegetarian thalis, paneer curries, and dal specialties.",
        "cuisine": "North Indian",
        "address": "Sarwate Bus Stand, South Tukoganj",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&auto=format&fit=crop&q=80",
        "rating": 4.5,
        "avg_cost_for_two": 400,
        "delivery_time": 25,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 1450,
        "menu_items": [
            {
                "title": "Paneer Butter Masala",
                "price": 240.0,
                "description": "Rich cottage cheese cubes cooked in tomato-cashew gravy with aromatic spices.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Hara Bhara Kebab",
                "price": 160.0,
                "description": "Crispy spinach and green pea patties stuffed with mild spices.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Butter Naan",
                "price": 45.0,
                "description": "Tandoor baked fluffy flatbread brushed with butter.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Gulab Jamun (2 Pcs)",
                "price": 80.0,
                "description": "Soft golden mawa dumplings soaked in cardamom sugar syrup.",
                "category": "Desserts",
                "image_url": "https://images.unsplash.com/photo-1667789397941-657d478cf8e9?w=600&auto=format&fit=crop&q=80",
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Masala Chaas",
                "price": 50.0,
                "description": "Chilled spiced buttermilk with roasted cumin and mint.",
                "category": "Beverages",
                "image_url": "https://images.unsplash.com/photo-1556881286-fc6915169721?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Johnny Hot Dog",
        "description": "Famous street delicacies from 56 Dukan.",
        "cuisine": "Street Food",
        "address": "56 Dukan, New Palasia",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1627054234597-90c767e76535?w=800&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "avg_cost_for_two": 180,
        "delivery_time": 20,
        "is_pure_veg": False,
        "is_open": True,
        "order_count": 3400,
        "menu_items": [
            {
                "title": "Egg Benjo",
                "price": 50.0,
                "description": "Soft toasted bun sandwiching fluffy masala omelette.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=600&auto=format&fit=crop&q=80",
                "is_veg": False,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Mutton Hot Dog",
                "price": 90.0,
                "description": "Spicy minced mutton patty served inside hot buttered bun.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1627054234597-90c767e76535?w=600&auto=format&fit=crop&q=80",
                "is_veg": False,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Veg Cheese Burger",
                "price": 60.0,
                "description": "Crispy spiced vegetable cutlet layered with melting cheese.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Cold Coffee with Ice Cream",
                "price": 70.0,
                "description": "Rich blended iced coffee topped with a creamy vanilla scoop.",
                "category": "Beverages",
                "image_url": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Little Italy Trattoria",
        "description": "Wood-fired pizzas, handmade pastas, and Italian desserts.",
        "cuisine": "Italian",
        "address": "Vijay Nagar, Scheme 54",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80",
        "rating": 4.4,
        "avg_cost_for_two": 900,
        "delivery_time": 30,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 890,
        "menu_items": [
            {
                "title": "Margherita Pizza (10 inch)",
                "price": 380.0,
                "description": "Wood-fired crust topped with San Marzano tomato sauce, fresh mozzarella, and basil.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Penne Alfredo",
                "price": 340.0,
                "description": "Penne pasta tossed in creamy parmesan and garlic white sauce with mushrooms.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Garlic Bread with Cheese",
                "price": 180.0,
                "description": "Toasted Italian baguette brushed with herb butter and melted mozzarella.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1619895092538-128341789043?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Classic Tiramisu",
                "price": 220.0,
                "description": "Coffee-soaked ladyfingers layered with mascarpone cream and dark cocoa.",
                "category": "Desserts",
                "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Bake Factory & Cafe",
        "description": "Artisan bakery items, sandwiches, shakes, and specialty coffee.",
        "cuisine": "Fast Food & Desserts",
        "address": "Geeta Bhawan Square",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80",
        "rating": 4.6,
        "avg_cost_for_two": 450,
        "delivery_time": 20,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 1650,
        "menu_items": [
            {
                "title": "Belgian Chocolate Pastry",
                "price": 120.0,
                "description": "Rich dark chocolate sponge layered with smooth chocolate ganache.",
                "category": "Desserts",
                "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Paneer Tikka Sandwich",
                "price": 140.0,
                "description": "Grilled brown bread sandwich packed with smoky spiced paneer and mint mayo.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Loaded Cheese Fries",
                "price": 130.0,
                "description": "Crispy french fries drenched in warm cheddar sauce and jalapenos.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Hazelnut Frappe",
                "price": 160.0,
                "description": "Creamy blended iced espresso infused with hazelnut syrup.",
                "category": "Beverages",
                "image_url": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed initial restaurants, menu items, coupons, and sample reviews"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting restaurant and menu seeding...")

        demo_user, _ = User.objects.get_or_create(
            mobile="9876543210",
            defaults={
                "full_name": "Aman Sharma",
                "email": "aman@example.com",
                "default_address": "Flat 402, Sunshine Heights, Indore",
            }
        )

        total_restaurants = 0
        total_items = 0

        for r_data in RESTAURANTS_DATA:
            items = r_data.pop("menu_items", None) or r_data.pop("items", [])

            restaurant, _ = Restaurant.objects.update_or_create(
                name=r_data["name"],
                city=r_data["city"],
                defaults=r_data
            )
            total_restaurants += 1

            for item_data in items:
                cat = item_data.get("category", "Main Course")
                if cat in ("Starter", "starter"):
                    item_data["category"] = "Starters"

                MenuItem.objects.update_or_create(
                    restaurant=restaurant,
                    title=item_data["title"],
                    defaults=item_data
                )
                total_items += 1

            Review.objects.get_or_create(
                restaurant=restaurant,
                user=demo_user,
                defaults={
                    "rating": 5 if restaurant.rating >= 4.5 else 4,
                    "comment": f"Excellent food and speedy delivery from {restaurant.name}! Highly recommended."
                }
            )

        total_coupons = 0
        for c_data in COUPONS_DATA:
            Coupon.objects.update_or_create(
                code=c_data["code"],
                defaults=c_data
            )
            total_coupons += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {total_restaurants} restaurants, {total_items} menu items, and {total_coupons} promo coupons."
            )
        )
