from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import User, OTPVerification, Restaurant, MenuItem, Cart, Coupon


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_send_otp_success(self):
        response = self.client.post('/api/auth/send-otp/', {'mobile': '9876543210'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mobile'], '9876543210')
        self.assertEqual(response.data['otp'], '123456')
        self.assertTrue(OTPVerification.objects.filter(mobile='9876543210').exists())

    def test_verify_otp_and_login(self):
        self.client.post('/api/auth/send-otp/', {'mobile': '9876543210'}, format='json')

        response = self.client.post('/api/auth/verify-otp/', {
            'mobile': '9876543210',
            'otp': '123456',
            'name': 'Rahul Verma'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['full_name'], 'Rahul Verma')

        user = User.objects.get(mobile='9876543210')
        self.assertEqual(user.full_name, 'Rahul Verma')


class RestaurantFilterAndSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.r1 = Restaurant.objects.create(
            name="Nafees Restaurant",
            cuisine="North Indian",
            rating=Decimal("4.5"),
            avg_cost_for_two=600,
            is_pure_veg=False,
            is_open=True,
            city="Indore",
            delivery_time=25
        )
        self.r2 = Restaurant.objects.create(
            name="Guru Kripa Restaurant",
            cuisine="South Indian",
            rating=Decimal("4.8"),
            avg_cost_for_two=350,
            is_pure_veg=True,
            is_open=True,
            city="Indore",
            delivery_time=20
        )
        self.r3 = Restaurant.objects.create(
            name="Mumbai Express",
            cuisine="Fast Food",
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

    def test_search_by_menu_item_title(self):
        response = self.client.get('/api/restaurants/?search=Butter Chicken')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Nafees Restaurant")


class CartAndOrderTests(TestCase):
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
        self.coupon = Coupon.objects.create(
            code="SAVE50",
            description="50% off up to 100",
            discount_type="PERCENT",
            discount_value=Decimal("50.00"),
            min_order_amount=Decimal("200.00"),
            max_discount=Decimal("100.00"),
            is_active=True
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

    def test_cross_restaurant_conflict(self):
        self.client.post('/api/cart/', {'menu_item_id': self.item1.id, 'quantity': 1}, format='json')

        response = self.client.post('/api/cart/', {'menu_item_id': self.item2.id, 'quantity': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(response.data['conflict'])

        response = self.client.post('/api/cart/', {
            'menu_item_id': self.item2.id,
            'quantity': 1,
            'clear_existing': True
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Cart.objects.filter(user=self.user).first().restaurant, self.r2)

    def test_apply_coupon_validation(self):
        res_fail = self.client.post('/api/coupons/apply/', {
            'code': 'SAVE50',
            'item_total': 150.00
        }, format='json')
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

        res_success = self.client.post('/api/coupons/apply/', {
            'code': 'SAVE50',
            'item_total': 280.00
        }, format='json')
        self.assertEqual(res_success.status_code, status.HTTP_200_OK)
        self.assertEqual(res_success.data['discount_amount'], 100.0)

    def test_place_order_with_coupon_and_razorpay_flow(self):
        self.client.post('/api/cart/', {'menu_item_id': self.item1.id, 'quantity': 1}, format='json')

        response = self.client.post('/api/orders/', {
            'delivery_address': 'Flat 101, Green Meadows, Indore',
            'payment_mode': 'Razorpay',
            'coupon_code': 'SAVE50'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']
        self.assertEqual(response.data['order_status'], 'PLACED')
        self.assertEqual(response.data['coupon_code'], 'SAVE50')
        self.assertEqual(response.data['grand_total'], '234.00')
        self.assertEqual(response.data['payment_status'], 'PENDING')

        rzp_order_resp = self.client.post('/api/payments/create-razorpay-order/', {
            'order_id': order_id
        }, format='json')
        self.assertEqual(rzp_order_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(rzp_order_resp.data['amount'], 23400)

        verify_resp = self.client.post('/api/payments/verify-razorpay-payment/', {
            'order_id': order_id,
            'razorpay_payment_id': 'pay_test_999888777',
            'razorpay_order_id': rzp_order_resp.data['razorpay_order_id'],
        }, format='json')
        self.assertEqual(verify_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(verify_resp.data['order']['payment_status'], 'PAID')
        self.assertEqual(verify_resp.data['order']['transaction_id'], 'pay_test_999888777')
