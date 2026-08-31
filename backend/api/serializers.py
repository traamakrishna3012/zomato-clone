from decimal import Decimal
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from .models import User, OTPVerification, Restaurant, MenuItem, Cart, Order, OrderItem, Review, Coupon


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'mobile', 'full_name', 'email', 'default_address', 'created_at')
        read_only_fields = ('id', 'mobile', 'created_at')


class OTPRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)

    def validate_mobile(self, value):
        cleaned = value.strip().replace(" ", "").replace("-", "")
        if not cleaned.isdigit() or len(cleaned) < 10:
            raise serializers.ValidationError("Please provide a valid 10-digit mobile number.")
        return cleaned


class OTPVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
    name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_otp(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return value


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = (
            'id',
            'restaurant',
            'title',
            'description',
            'price',
            'category',
            'is_veg',
            'image_url',
            'is_bestseller',
            'is_available',
            'created_at',
        )


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'restaurant', 'user', 'user_name', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'user', 'user_name', 'created_at')

    @extend_schema_field(OpenApiTypes.STR)
    def get_user_name(self, obj):
        return obj.user.full_name or f"User {obj.user.mobile[-4:]}"


class RestaurantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'id',
            'name',
            'description',
            'cuisine',
            'rating',
            'avg_cost_for_two',
            'is_pure_veg',
            'is_open',
            'image_url',
            'address',
            'city',
            'delivery_time',
            'order_count',
            'created_at',
        )


class RestaurantDetailSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = (
            'id',
            'name',
            'description',
            'cuisine',
            'rating',
            'avg_cost_for_two',
            'is_pure_veg',
            'is_open',
            'image_url',
            'address',
            'city',
            'delivery_time',
            'order_count',
            'menu_items',
            'reviews',
            'created_at',
        )


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'restaurant', 'restaurant_name', 'menu_item', 'quantity', 'subtotal')
        read_only_fields = ('id', 'restaurant', 'restaurant_name', 'menu_item', 'subtotal')

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_subtotal(self, obj):
        return round(float(obj.menu_item.price * obj.quantity), 2)


class AddToCartSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    clear_existing = serializers.BooleanField(default=False)

    def validate_menu_item_id(self, value):
        try:
            item = MenuItem.objects.select_related('restaurant').get(id=value)
            if not item.is_available:
                raise serializers.ValidationError("This menu item is currently unavailable.")
            return item
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError("Menu item not found.")


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'menu_item', 'item_title', 'price', 'quantity', 'subtotal')

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_subtotal(self, obj):
        return round(float(obj.price * obj.quantity), 2)


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            'id',
            'code',
            'description',
            'discount_type',
            'discount_value',
            'min_order_amount',
            'max_discount',
            'is_active',
        )


class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)
    item_total = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_image = serializers.CharField(source='restaurant.image_url', read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'restaurant',
            'restaurant_name',
            'restaurant_image',
            'order_status',
            'payment_mode',
            'payment_status',
            'transaction_id',
            'razorpay_order_id',
            'coupon',
            'coupon_code',
            'discount_amount',
            'item_total',
            'taxes',
            'delivery_fee',
            'grand_total',
            'delivery_address',
            'items',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'order_status',
            'payment_status',
            'transaction_id',
            'razorpay_order_id',
            'discount_amount',
            'item_total',
            'taxes',
            'delivery_fee',
            'grand_total',
            'items',
            'created_at',
            'updated_at',
        )


class CreateOrderItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField(max_length=500)
    payment_mode = serializers.ChoiceField(
        choices=Order.PAYMENT_CHOICES,
        default='COD'
    )
    coupon_code = serializers.CharField(max_length=30, required=False, allow_blank=True)
    items = CreateOrderItemSerializer(many=True, required=False)


class RazorpayCreateOrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()


class RazorpayVerifySerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    razorpay_payment_id = serializers.CharField(max_length=100)
    razorpay_order_id = serializers.CharField(max_length=100)
    razorpay_signature = serializers.CharField(max_length=200, required=False, allow_blank=True)
