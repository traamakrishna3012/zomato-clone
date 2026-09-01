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
        "description": "Flat ₹100 OFF on orders above ₹299",
        "discount_type": "FLAT",
        "discount_value": 100.00,
        "min_order_amount": 299.00,
        "max_discount": None,
        "is_active": True,
    },
    {
        "code": "HUNGRY20",
        "description": "20% OFF up to ₹150 on orders above ₹249",
        "discount_type": "PERCENT",
        "discount_value": 20.00,
        "min_order_amount": 249.00,
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
        "name": "Nafees Restaurant",
        "description": "Authentic Mughlai curries, fragrant biryanis, and tandoori grills.",
        "cuisine": "Mughlai & North Indian",
        "address": "Apollo Tower, Old Palasia",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&auto=format&fit=crop&q=80",
        "rating": 4.5,
        "avg_cost_for_two": 650,
        "delivery_time": 35,
        "is_pure_veg": False,
        "is_open": True,
        "order_count": 2100,
        "menu_items": [
            {
                "title": "Mutton Dum Biryani",
                "price": 320.0,
                "description": "Slow cooked basmati rice with marinated mutton cuts and saffron aroma.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80",
                "is_veg": False,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Butter Chicken",
                "price": 280.0,
                "description": "Roasted chicken pieces in velvety butter, tomato, and cashew gravy.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=600&auto=format&fit=crop&q=80",
                "is_veg": False,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Murgh Malai Tikka",
                "price": 240.0,
                "description": "Boneless chicken marinated with cream, cheese, and mild spices grilled in tandoor.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=600&auto=format&fit=crop&q=80",
                "is_veg": False,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Butter Garlic Naan",
                "price": 50.0,
                "description": "Refined flour flatbread topped with garlic and butter, baked in clay oven.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Shahi Phirni",
                "price": 85.0,
                "description": "Traditional chilled rice pudding infused with saffron, cardamom, and pistachios.",
                "category": "Desserts",
                "image_url": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Guru Kripa Restaurant",
        "description": "Traditional pure vegetarian North Indian curries, thalis, and breads.",
        "cuisine": "North Indian",
        "address": "Sarwate Bus Stand, South Tukoganj",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&auto=format&fit=crop&q=80",
        "rating": 4.6,
        "avg_cost_for_two": 400,
        "delivery_time": 25,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 3800,
        "menu_items": [
            {
                "title": "Special Paneer Butter Masala",
                "price": 230.0,
                "description": "Fresh malai paneer cubes simmered in spiced tomato cashew gravy.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Sev Tamatar",
                "price": 160.0,
                "description": "Classic Indori style spicy tomato curry topped with crisp ratlami sev.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Hara Bhara Kebab",
                "price": 150.0,
                "description": "Pan-fried patties made with spinach, green peas, and potatoes.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Tandoori Butter Roti",
                "price": 20.0,
                "description": "Whole wheat bread baked in tandoor with fresh butter.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Gulab Jamun (2 pcs)",
                "price": 70.0,
                "description": "Fried milk dough dumplings soaked in fragrant cardamom sugar syrup.",
                "category": "Desserts",
                "image_url": "https://images.unsplash.com/photo-1667789397941-657d478cf8e9?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Masala Chaas",
                "price": 40.0,
                "description": "Chilled spiced buttermilk with roasted cumin and fresh coriander.",
                "category": "Beverages",
                "image_url": "https://images.unsplash.com/photo-1556881286-fc6915169721?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Vijay Chaat House",
        "description": "Famous street food delicacies from Sarafa Bazaar and 56 Dukan.",
        "cuisine": "Street Food & Chaat",
        "address": "56 Dukan, New Palasia",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "avg_cost_for_two": 200,
        "delivery_time": 20,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 4500,
        "menu_items": [
            {
                "title": "Indori Khopra Patties (2 pcs)",
                "price": 70.0,
                "description": "Crisp potato patties stuffed with spiced coconut filling, served with sweet chutney.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Poha Jalebi Combo",
                "price": 60.0,
                "description": "Steamed seasoned flattened rice with jeeravan masala, sev, and 2 hot jalebis.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Khatta Meetha Shikanji",
                "price": 50.0,
                "description": "Signature thick spiced sweet yogurt drink with dry fruits.",
                "category": "Beverages",
                "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Crispy Garadu Chaat",
                "price": 80.0,
                "description": "Fried yam tossed with fresh lemon and authentic spicy chaat masala.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Dragon Wok",
        "description": "Indo-Chinese street noodles, fried rice, and gravies.",
        "cuisine": "Chinese",
        "address": "Scheme 54, Vijay Nagar",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&auto=format&fit=crop&q=80",
        "rating": 4.2,
        "avg_cost_for_two": 450,
        "delivery_time": 30,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 1300,
        "menu_items": [
            {
                "title": "Veg Hakka Noodles",
                "price": 170.0,
                "description": "Wok-tossed noodles with shredded cabbage, bell peppers, carrots, and soy seasoning.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Chilli Paneer Dry",
                "price": 210.0,
                "description": "Crisp batter-fried paneer cubes tossed in spicy soy-chili sauce with scallions.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Veg Manchurian Gravy",
                "price": 180.0,
                "description": "Minced veggie balls in a dark garlic, chili, and cilantro sauce.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1525755662778-989d0524087e?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Crispy Spring Rolls (4 pcs)",
                "price": 140.0,
                "description": "Golden fried rolls stuffed with seasoned julienned vegetables.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Iced Lemon Green Tea",
                "price": 75.0,
                "description": "Chilled green tea infused with fresh lemon extract and mint.",
                "category": "Beverages",
                "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Little Italy",
        "description": "Wood-fired thin crust pizzas, creamy pastas, and desserts.",
        "cuisine": "Italian",
        "address": "Near Meghdoot Garden, Vijay Nagar",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80",
        "rating": 4.4,
        "avg_cost_for_two": 850,
        "delivery_time": 30,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 920,
        "menu_items": [
            {
                "title": "Margherita Pizza (10 inch)",
                "price": 360.0,
                "description": "Classic thin crust with San Marzano sauce, fresh mozzarella, and basil leaves.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Penne Alfredo Pasta",
                "price": 320.0,
                "description": "Penne pasta in creamy garlic white sauce with sautéed mushrooms.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Garlic Bread with Cheese",
                "price": 160.0,
                "description": "Toasted baguette bread brushed with garlic butter and melted mozzarella.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1619895092538-128341789043?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Classic Tiramisu",
                "price": 210.0,
                "description": "Coffee-soaked ladyfingers with whipped mascarpone cheese and cocoa dust.",
                "category": "Desserts",
                "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
        ],
    },
    {
        "name": "Bake N Shake",
        "description": "Artisan burgers, sandwiches, pastries, and thick milkshakes.",
        "cuisine": "Fast Food & Bakery",
        "address": "Geeta Bhawan Square, AB Road",
        "city": "Indore",
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80",
        "rating": 4.6,
        "avg_cost_for_two": 450,
        "delivery_time": 25,
        "is_pure_veg": True,
        "is_open": True,
        "order_count": 1750,
        "menu_items": [
            {
                "title": "Paneer Tikka Grilled Sandwich",
                "price": 140.0,
                "description": "Jumbo brown bread filled with spiced paneer tikka, capsicum, and mint mayo.",
                "category": "Main Course",
                "image_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Loaded Cheesy Fries",
                "price": 130.0,
                "description": "Crispy salted potato fries covered with warm liquid cheese and peri-peri seasoning.",
                "category": "Starters",
                "image_url": "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": False,
                "is_available": True,
            },
            {
                "title": "Belgian Chocolate Pastry",
                "price": 110.0,
                "description": "Dark chocolate sponge layered with rich cocoa truffle ganache.",
                "category": "Desserts",
                "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop&q=80",
                "is_veg": True,
                "is_bestseller": True,
                "is_available": True,
            },
            {
                "title": "Hazelnut Cold Coffee",
                "price": 150.0,
                "description": "Thick blended cold coffee flavored with roasted hazelnut syrup.",
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
    help = "Seed initial restaurants, menu items, promo coupons, and sample reviews"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding restaurants, menus, and coupons...")

        demo_user, _ = User.objects.get_or_create(
            mobile="9876543210",
            defaults={
                                "full_name": "Zomato User",
                "email": "zomato@example.com",
                "default_address": "Flat 402, Sunshine Heights, Indore",
            }
        )
        
        # Check if admin superuser exists
        admin_user, created = User.objects.get_or_create(
            mobile="9999999999",
            defaults={
                "full_name": "Admin User",
                "email": "admin@zomato-clone.local",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created or not admin_user.has_usable_password():
            admin_user.set_password("admin123")
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

        restaurant_count = 0
        menu_item_count = 0

        for restaurant_entry in RESTAURANTS_DATA:
            menu_items_list = restaurant_entry.pop("menu_items", [])

            restaurant, _ = Restaurant.objects.update_or_create(
                name=restaurant_entry["name"],
                city=restaurant_entry["city"],
                defaults=restaurant_entry
            )
            restaurant_count += 1

            for item_entry in menu_items_list:
                MenuItem.objects.update_or_create(
                    restaurant=restaurant,
                    title=item_entry["title"],
                    defaults=item_entry
                )
                menu_item_count += 1

            Review.objects.get_or_create(
                restaurant=restaurant,
                user=demo_user,
                defaults={
                    "rating": 5 if restaurant.rating >= 4.5 else 4,
                    "comment": f"Great taste and fast delivery from {restaurant.name}!"
                }
            )

        coupon_count = 0
        for coupon_entry in COUPONS_DATA:
            Coupon.objects.update_or_create(
                code=coupon_entry["code"],
                defaults=coupon_entry
            )
            coupon_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {restaurant_count} restaurants, {menu_item_count} menu items, and {coupon_count} coupons."
            )
        )
