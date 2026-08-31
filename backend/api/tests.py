from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from .models import User, OTPVerification, Restaurant, MenuItem, Cart, Order, Review, Coupon


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_send_and_verify_otp_flow(self):
        # 1. Send OTP
        res_send = self.client.post('/api/auth/send-otp/', {'mobile': '9876543210'}, format='json')
        self.assertEqual(res_send.status_code, status.HTTP_200_OK)
        self.assertEqual(res_send.data['mobile'], '9876543210')

        # Verify OTP was stored in DB
        otp_record = OTPVerification.objects.filter(mobile='9876543210', is_verified=False).first()
        self.assertIsNotNone(otp_record)
        generated_otp = otp_record.otp
        self.assertEqual(len(generated_otp), 6)

        # 2. Verify OTP with correct code
        res_verify = self.client.post('/api/auth/verify-otp/', {
            'mobile': '9876543210',
            'otp': generated_otp,
            'name': 'Rahul Verma'
        }, format='json')

        self.assertEqual(res_verify.status_code, status.HTTP_200_OK)
        self.assertIn('access', res_verify.data)
        self.assertIn('refresh', res_verify.data)
        self.assertTrue(res_verify.data['is_new_user'])
        self.assertEqual(res_verify.data['user']['full_name'], 'Rahul Verma')

        # 3. Verify OTP is marked consumed and cannot be reused
        otp_record.refresh_from_db()
        self.assertTrue(otp_record.is_verified)

        res_reuse = self.client.post('/api/auth/verify-otp/', {
            'mobile': '9876543210',
            'otp': generated_otp,
        }, format='json')
        self.assertEqual(res_reuse.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_otp_rejection(self):
        otp_record = OTPVerification.objects.create(
            mobile='9876543210',
            otp='654321',
            is_verified=False
        )
        # Artificially age the record past 5 minutes
        OTPVerification.objects.filter(id=otp_record.id).update(
            created_at=timezone.now() - timedelta(minutes=6)
        )

        response = self.client.post('/api/auth/verify-otp/', {
            'mobile': '9876543210',
            'otp': '654321'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_otp_invalid_mobile(self):
        response = self.client.post('/api/auth/send-otp/', {'mobile': '123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_profile_access(self):
        user = User.objects.create_user(mobile="9876543210", full_name="Aman Sharma")
        
        # Unauthenticated request
        res_unauth = self.client.get('/api/auth/profile/')
        self.assertEqual(res_unauth.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated request
        self.client.force_authenticate(user=user)
        res_auth = self.client.get('/api/auth/profile/')
        self.assertEqual(res_auth.status_code, status.HTTP_200_OK)
        self.assertEqual(res_auth.data['full_name'], "Aman Sharma")


class RestaurantDiscoveryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r1 = Restaurant.objects.create(
            name="Nafees Restaurant",
            cuisine="Mughlai",
            rating=Decimal("4.6"),
            avg_cost_for_two=600,
            is_pure_veg=False,
            is_open=True,
            city="Indore",
            delivery_time=25
        )
        self.r2 = Restaurant.objects.create(
            name="Guru Kripa Restaurant",
            cuisine="North Indian",
            rating=Decimal("4.8"),
            avg_cost_for_two=350,
            is_pure_veg=True,
            is_open=True,
            city="Indore",
            delivery_time=20
        )
        self.r3 = Restaurant.objects.create(
            name="Mumbai Express",
            cuisine="Street Food",
            rating=Decimal("3.8"),
            avg_cost_for_two=250,
            is_pure_veg=True,
            is_open=True,
            city="Mumbai",
            delivery_time=45
        )
        MenuItem.objects.create(
            restaurant=self.r1,
            title="Butter Chicken",
            price=Decimal("280.00"),
            category="Main Course",
            is_veg=False
        )

    def test_filter_by_city(self):
        response = self.client.get('/api/restaurants/?city=Indore')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        restaurant_names = [item['name'] for item in response.data['results']]
        self.assertIn("Nafees Restaurant", restaurant_names)
        self.assertIn("Guru Kripa Restaurant", restaurant_names)
        self.assertNotIn("Mumbai Express", restaurant_names)

    def test_filter_by_pure_veg(self):
        response = self.client.get('/api/restaurants/?is_pure_veg=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for restaurant in response.data['results']:
            self.assertTrue(restaurant['is_pure_veg'])

    def test_filter_by_min_rating(self):
        response = self.client.get('/api/restaurants/?min_rating=4.0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for restaurant in response.data['results']:
            self.assertGreaterEqual(float(restaurant['rating']), 4.0)

    def test_search_by_dish_name(self):
        response = self.client.get('/api/restaurants/?search=Butter Chicken')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Nafees Restaurant")

    def test_top_picks_endpoint(self):
        response = self.client.get('/api/restaurants/top-picks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for r in response.data:
            self.assertGreaterEqual(float(r['rating']), 4.0)


class CartBusinessRuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(mobile="9998887770", full_name="Test User")
        self.client.force_authenticate(user=self.user)

        self.r1 = Restaurant.objects.create(
            name="Restaurant One",
            cuisine="North Indian",
            rating=Decimal("4.5"),
            city="Indore"
        )
        self.r2 = Restaurant.objects.create(
            name="Restaurant Two",
            cuisine="Chinese",
            rating=Decimal("4.2"),
            city="Indore"
        )
        self.item1 = MenuItem.objects.create(
            restaurant=self.r1,
            title="Paneer Tikka",
            price=Decimal("280.00"),
            is_available=True
        )
        self.item2 = MenuItem.objects.create(
            restaurant=self.r2,
            title="Hakka Noodles",
            price=Decimal("180.00"),
            is_available=True
        )
        self.unavailable_item = MenuItem.objects.create(
            restaurant=self.r1,
            title="Special Sweet",
            price=Decimal("120.00"),
            is_available=False
        )

    def test_add_to_cart_and_calculate_summary(self):
        response = self.client.post('/api/cart/', {
            'menu_item_id': self.item1.id,
            'quantity': 2
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        summary = self.client.get('/api/cart/summary/')
        self.assertEqual(summary.status_code, status.HTTP_200_OK)
        self.assertEqual(summary.data['item_count'], 2)
        self.assertEqual(summary.data['item_total'], 560.0)
        self.assertEqual(summary.data['taxes'], 28.0)
        self.assertEqual(summary.data['delivery_fee'], 40.0)
        self.assertEqual(summary.data['grand_total'], 628.0)

    def test_cannot_add_unavailable_menu_item(self):
        response = self.client.post('/api/cart/', {
            'menu_item_id': self.unavailable_item.id,
            'quantity': 1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_quantity_and_zero_removal(self):
        self.client.post('/api/cart/', {'menu_item_id': self.item1.id, 'quantity': 2}, format='json')
        cart_entry = Cart.objects.get(user=self.user, menu_item=self.item1)

        # Update quantity to 4
        res_update = self.client.patch(f'/api/cart/{cart_entry.id}/', {'quantity': 4}, format='json')
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
        self.assertEqual(res_update.data['quantity'], 4)

        # Update quantity to 0 removes entry
        res_remove = self.client.patch(f'/api/cart/{cart_entry.id}/', {'quantity': 0}, format='json')
        self.assertEqual(res_remove.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cart.objects.filter(id=cart_entry.id).exists())

    def test_cross_restaurant_conflict(self):
        self.client.post('/api/cart/', {'menu_item_id': self.item1.id, 'quantity': 1}, format='json')

        # Adding from second restaurant triggers 409 Conflict
        response = self.client.post('/api/cart/', {'menu_item_id': self.item2.id, 'quantity': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(response.data['conflict'])

        # Explicitly passing clear_existing=True resets cart to new restaurant
        response = self.client.post('/api/cart/', {
            'menu_item_id': self.item2.id,
            'quantity': 1,
            'clear_existing': True
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Cart.objects.filter(user=self.user).first().restaurant, self.r2)


class CouponAndOrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(mobile="9998887770", full_name="Test User")
        self.client.force_authenticate(user=self.user)

        self.r1 = Restaurant.objects.create(
            name="Nafees Restaurant",
            cuisine="North Indian",
            rating=Decimal("4.5"),
            city="Indore"
        )
        self.r2 = Restaurant.objects.create(
            name="Guru Kripa",
            cuisine="North Indian",
            rating=Decimal("4.8"),
            city="Indore"
        )
        self.item1 = MenuItem.objects.create(
            restaurant=self.r1,
            title="Biryani",
            price=Decimal("300.00"),
            is_available=True
        )
        self.item2 = MenuItem.objects.create(
            restaurant=self.r2,
            title="Dal Makhani",
            price=Decimal("200.00"),
            is_available=True
        )
        self.coupon = Coupon.objects.create(
            code="SAVE50",
            description="50% off up to 100",
            discount_type="PERCENT",
            discount_value=Decimal("50.00"),
            min_order_amount=Decimal("250.00"),
            max_discount=Decimal("100.00"),
            is_active=True
        )

    def test_apply_coupon_rules(self):
        # Below min order amount
        res_fail = self.client.post('/api/coupons/apply/', {
            'code': 'SAVE50',
            'item_total': 200.00
        }, format='json')
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

        # Meets min spend -> capped at max discount ₹100
        res_success = self.client.post('/api/coupons/apply/', {
            'code': 'SAVE50',
            'item_total': 300.00
        }, format='json')
        self.assertEqual(res_success.status_code, status.HTTP_200_OK)
        self.assertEqual(res_success.data['discount_amount'], 100.0)

    def test_place_order_from_cart_and_clear(self):
        self.client.post('/api/cart/', {'menu_item_id': self.item1.id, 'quantity': 1}, format='json')

        response = self.client.post('/api/orders/', {
            'delivery_address': 'Flat 101, Green Meadows, Indore',
            'payment_mode': 'COD',
            'coupon_code': 'SAVE50'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['grand_total'], '255.00')
        self.assertEqual(response.data['payment_status'], 'PENDING')
        self.assertEqual(response.data['order_status'], 'PLACED')

        # Verify user cart is cleared
        self.assertFalse(Cart.objects.filter(user=self.user).exists())

    def test_reject_mixed_restaurant_custom_payload(self):
        response = self.client.post('/api/orders/', {
            'delivery_address': 'Indore',
            'payment_mode': 'COD',
            'items': [
                {'menu_item_id': self.item1.id, 'quantity': 1},
                {'menu_item_id': self.item2.id, 'quantity': 1},
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_cancellation_constraints(self):
        order = Order.objects.create(
            user=self.user,
            restaurant=self.r1,
            order_status='PLACED',
            item_total=Decimal("300.00"),
            grand_total=Decimal("355.00"),
            delivery_address="Indore"
        )

        # Cancellation allowed in PLACED stage
        res_cancel = self.client.post(f'/api/orders/{order.id}/cancel/')
        self.assertEqual(res_cancel.status_code, status.HTTP_200_OK)
        self.assertEqual(res_cancel.data['order']['order_status'], 'CANCELLED')

        # Cannot cancel once PREPARING or DELIVERED
        order.order_status = 'PREPARING'
        order.save()
        res_invalid_cancel = self.client.post(f'/api/orders/{order.id}/cancel/')
        self.assertEqual(res_invalid_cancel.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_stage_progression(self):
        order = Order.objects.create(
            user=self.user,
            restaurant=self.r1,
            order_status='PLACED',
            item_total=Decimal("300.00"),
            grand_total=Decimal("355.00"),
            delivery_address="Indore"
        )

        # PLACED -> PREPARING
        res_1 = self.client.post(f'/api/orders/{order.id}/progress-status/')
        self.assertEqual(res_1.data['order_status'], 'PREPARING')

        # PREPARING -> OUT_FOR_DELIVERY
        res_2 = self.client.post(f'/api/orders/{order.id}/progress-status/')
        self.assertEqual(res_2.data['order_status'], 'OUT_FOR_DELIVERY')

        # OUT_FOR_DELIVERY -> DELIVERED
        res_3 = self.client.post(f'/api/orders/{order.id}/progress-status/')
        self.assertEqual(res_3.data['order_status'], 'DELIVERED')

    def test_razorpay_payment_flow(self):
        order = Order.objects.create(
            user=self.user,
            restaurant=self.r1,
            order_status='PLACED',
            payment_mode='Razorpay',
            payment_status='PENDING',
            item_total=Decimal("300.00"),
            grand_total=Decimal("355.00"),
            delivery_address="Indore"
        )

        # Create test order
        rzp_res = self.client.post('/api/payments/create-razorpay-order/', {'order_id': order.id}, format='json')
        self.assertEqual(rzp_res.status_code, status.HTTP_200_OK)
        self.assertEqual(rzp_res.data['amount'], 35500)

        # Verify payment
        verify_res = self.client.post('/api/payments/verify-razorpay-payment/', {
            'order_id': order.id,
            'razorpay_payment_id': 'pay_test_12345',
            'razorpay_order_id': rzp_res.data['razorpay_order_id'],
        }, format='json')
        self.assertEqual(verify_res.status_code, status.HTTP_200_OK)
        self.assertEqual(verify_res.data['order']['payment_status'], 'PAID')

    def test_cannot_pay_already_paid_order(self):
        order = Order.objects.create(
            user=self.user,
            restaurant=self.r1,
            order_status='PLACED',
            payment_mode='Razorpay',
            payment_status='PAID',
            item_total=Decimal("300.00"),
            grand_total=Decimal("355.00"),
            delivery_address="Indore"
        )
        rzp_res = self.client.post('/api/payments/create-razorpay-order/', {'order_id': order.id}, format='json')
        self.assertEqual(rzp_res.status_code, status.HTTP_400_BAD_REQUEST)


class ReviewRatingAggregationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(mobile="9998887770", full_name="Food Critic")
        self.client.force_authenticate(user=self.user)

        self.restaurant = Restaurant.objects.create(
            name="Nafees Restaurant",
            cuisine="North Indian",
            rating=Decimal("4.0"),
            city="Indore"
        )

    def test_review_recalculates_average_rating(self):
        self.client.post('/api/reviews/', {
            'restaurant': self.restaurant.id,
            'rating': 5,
            'comment': 'Exceptional food!'
        }, format='json')

        self.restaurant.refresh_from_db()
        self.assertEqual(float(self.restaurant.rating), 5.0)
