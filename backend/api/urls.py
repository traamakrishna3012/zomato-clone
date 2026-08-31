from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SendOTPView,
    VerifyOTPView,
    UserProfileView,
    RestaurantViewSet,
    CartViewSet,
    OrderViewSet,
    ReviewViewSet,
    CouponViewSet,
    RazorpayCreateOrderView,
    RazorpayVerifyPaymentView,
)

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('auth/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),

    path('payments/create-razorpay-order/', RazorpayCreateOrderView.as_view(), name='razorpay-create-order'),
    path('payments/verify-razorpay-payment/', RazorpayVerifyPaymentView.as_view(), name='razorpay-verify-payment'),

    path('', include(router.urls)),
]
