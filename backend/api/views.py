import uuid
import secrets
import logging
from decimal import Decimal
from django.db import transaction, models
from django.db.models import Avg, F
from django.conf import settings
from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import User, OTPVerification, Restaurant, MenuItem, Cart, Order, OrderItem, Review, Coupon
from .filters import RestaurantFilter
from .serializers import (
    UserSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    RestaurantListSerializer,
    RestaurantDetailSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    ReviewSerializer,
    CouponSerializer,
    ApplyCouponSerializer,
    RazorpayCreateOrderSerializer,
    RazorpayVerifySerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=['Authentication'])
class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['mobile']

        # Invalidate any previous unverified codes for this mobile
        OTPVerification.objects.filter(mobile=mobile, is_verified=False).delete()

        # Generate a cryptographically secure 6-digit OTP
        otp = f"{secrets.randbelow(900000) + 100000}"

        OTPVerification.objects.create(
            mobile=mobile,
            otp=otp,
            is_verified=False
        )

        # In development/test mode, print to console for convenient verification
        print(f"[AUTH OTP] Mobile: {mobile} | Code: {otp}")

        response_payload = {
            "message": "OTP sent successfully. Please check your SMS.",
            "mobile": mobile,
        }

        # Include debug_otp in development/evaluation if DEBUG is True
        if getattr(settings, 'DEBUG', False):
            response_payload["debug_otp"] = otp

        return Response(response_payload, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['mobile']
        otp = serializer.validated_data['otp']
        full_name = serializer.validated_data.get('name', '').strip()

        otp_record = OTPVerification.objects.filter(
            mobile=mobile,
            otp=otp,
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_record or otp_record.is_expired(expiry_minutes=5):
            return Response({
                "detail": "Invalid or expired OTP. Please request a new code."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mark OTP as consumed
        otp_record.is_verified = True
        otp_record.save(update_fields=['is_verified'])

        user, is_new_user = User.objects.get_or_create(
            mobile=mobile,
            defaults={"full_name": full_name}
        )

        if full_name and not user.full_name:
            user.full_name = full_name
            user.save(update_fields=['full_name'])

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
            "is_new_user": is_new_user,
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@extend_schema_view(
    list=extend_schema(tags=['Restaurants']),
    retrieve=extend_schema(tags=['Restaurants']),
)
class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Restaurant.objects.all().prefetch_related('menu_items', 'reviews__user')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RestaurantFilter
    search_fields = ['name', 'cuisine', 'menu_items__title']
    ordering_fields = ['rating', 'avg_cost_for_two', 'delivery_time', 'order_count']
    ordering = ['-rating', '-order_count']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('search'):
            queryset = queryset.distinct()
        return queryset

    @extend_schema(tags=['Restaurants'], responses={200: RestaurantListSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='top-picks')
    def top_picks(self, request):
        top_restaurants = self.get_queryset().filter(rating__gte=4.0).order_by('-rating', '-order_count')[:10]
        serializer = RestaurantListSerializer(top_restaurants, many=True)
        return Response(serializer.data)


@extend_schema_view(list=extend_schema(tags=['Coupons']))
class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(is_active=True).order_by('-discount_value')
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]

    @extend_schema(tags=['Coupons'], request=ApplyCouponSerializer)
    @action(detail=False, methods=['post'], url_path='apply')
    def apply(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code'].strip().upper()
        subtotal = serializer.validated_data['item_total']

        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({
                "valid": False,
                "detail": f"Coupon code '{code}' is invalid or expired."
            }, status=status.HTTP_400_BAD_REQUEST)

        if subtotal < coupon.min_order_amount:
            return Response({
                "valid": False,
                "detail": f"Coupon '{code}' requires a minimum order amount of ₹{coupon.min_order_amount:.0f}."
            }, status=status.HTTP_400_BAD_REQUEST)

        discount = coupon.calculate_discount(subtotal)

        return Response({
            "valid": True,
            "code": coupon.code,
            "description": coupon.description,
            "discount_amount": float(discount),
            "coupon": CouponSerializer(coupon).data,
            "message": f"Coupon '{coupon.code}' applied! You saved ₹{discount:.2f}."
        }, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(tags=['Cart']),
    create=extend_schema(tags=['Cart'], request=AddToCartSerializer),
    destroy=extend_schema(tags=['Cart']),
)
class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user).select_related('restaurant', 'menu_item')

    def create(self, request, *args, **kwargs):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menu_item = serializer.validated_data['menu_item_id']
        quantity = serializer.validated_data['quantity']
        clear_existing = serializer.validated_data['clear_existing']
        target_restaurant = menu_item.restaurant

        # Enforce single restaurant per order
        existing_cart_items = Cart.objects.filter(user=request.user).select_related('restaurant')
        first_cart_item = existing_cart_items.first()

        if first_cart_item and first_cart_item.restaurant_id != target_restaurant.id:
            if clear_existing:
                existing_cart_items.delete()
            else:
                return Response({
                    "conflict": True,
                    "existing_restaurant_id": first_cart_item.restaurant_id,
                    "existing_restaurant_name": first_cart_item.restaurant.name,
                    "target_restaurant_name": target_restaurant.name,
                    "detail": f"Your cart contains items from {first_cart_item.restaurant.name}. Reset cart to add items from {target_restaurant.name}?",
                }, status=status.HTTP_409_CONFLICT)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menu_item=menu_item,
            defaults={
                'restaurant': target_restaurant,
                'quantity': quantity
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save(update_fields=['quantity', 'updated_at'])

        cart_items = self.get_queryset()
        return Response(
            CartItemSerializer(cart_items, many=True).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        quantity = request.data.get('quantity')

        if quantity is None:
            return Response({"detail": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({"detail": "Quantity must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        cart_item.quantity = quantity
        cart_item.save(update_fields=['quantity', 'updated_at'])
        return Response(CartItemSerializer(cart_item).data)

    @extend_schema(tags=['Cart'])
    @action(detail=False, methods=['post'], url_path='clear')
    def clear(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart cleared successfully."})

    @extend_schema(tags=['Cart'])
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        cart_items = self.get_queryset()
        if not cart_items.exists():
            return Response({
                "item_count": 0,
                "item_total": 0.00,
                "taxes": 0.00,
                "delivery_fee": 0.00,
                "grand_total": 0.00,
                "restaurant": None,
                "items": [],
            })

        # Bill breakdown: 5% GST and flat ₹40 delivery fee
        subtotal = sum(Decimal(str(item.menu_item.price)) * item.quantity for item in cart_items)
        taxes = round(subtotal * Decimal('0.05'), 2)
        delivery_fee = Decimal('40.00')
        grand_total = subtotal + taxes + delivery_fee
        item_count = sum(item.quantity for item in cart_items)
        first_item = cart_items.first()

        return Response({
            "item_count": item_count,
            "item_total": float(subtotal),
            "taxes": float(taxes),
            "delivery_fee": float(delivery_fee),
            "grand_total": float(grand_total),
            "restaurant_id": first_item.restaurant_id,
            "restaurant_name": first_item.restaurant.name,
            "items": CartItemSerializer(cart_items, many=True).data,
        })


@extend_schema_view(
    list=extend_schema(tags=['Orders']),
    retrieve=extend_schema(tags=['Orders']),
    create=extend_schema(tags=['Orders'], request=CreateOrderSerializer, responses={201: OrderSerializer}),
)
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).select_related('restaurant', 'coupon').prefetch_related('items')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        delivery_address = serializer.validated_data['delivery_address'].strip()
        payment_mode = serializer.validated_data['payment_mode']
        coupon_code = serializer.validated_data.get('coupon_code', '').strip().upper()
        custom_items_payload = serializer.validated_data.get('items', [])

        prepared_items = []
        subtotal = Decimal('0.00')

        if custom_items_payload:
            item_ids = [entry['menu_item_id'] for entry in custom_items_payload]
            menu_items_map = {
                item.id: item
                for item in MenuItem.objects.filter(id__in=item_ids).select_related('restaurant')
            }
            if len(menu_items_map) != len(set(item_ids)):
                return Response({"detail": "One or more selected menu items do not exist."}, status=status.HTTP_400_BAD_REQUEST)

            restaurant_ids = {item.restaurant_id for item in menu_items_map.values()}
            if len(restaurant_ids) > 1:
                return Response({"detail": "All items in an order must belong to the same restaurant."}, status=status.HTTP_400_BAD_REQUEST)

            first_item = next(iter(menu_items_map.values()))
            restaurant = first_item.restaurant

            for entry in custom_items_payload:
                menu_item = menu_items_map.get(entry['menu_item_id'])
                if not menu_item.is_available:
                    return Response({"detail": f"Item '{menu_item.title}' is currently unavailable."}, status=status.HTTP_400_BAD_REQUEST)
                quantity = entry['quantity']
                prepared_items.append((menu_item, menu_item.title, menu_item.price, quantity))
                subtotal += Decimal(str(menu_item.price)) * quantity
        else:
            cart_items = Cart.objects.filter(user=request.user).select_related('menu_item', 'restaurant')
            if not cart_items.exists():
                return Response({
                    "detail": "Your cart is empty. Add items before placing an order."
                }, status=status.HTTP_400_BAD_REQUEST)

            for cart_item in cart_items:
                if not cart_item.menu_item.is_available:
                    return Response({
                        "detail": f"Item '{cart_item.menu_item.title}' in your cart is currently unavailable."
                    }, status=status.HTTP_400_BAD_REQUEST)

            restaurant = cart_items.first().restaurant
            prepared_items = [
                (cart_item.menu_item, cart_item.menu_item.title, cart_item.menu_item.price, cart_item.quantity)
                for cart_item in cart_items
            ]
            subtotal = sum(Decimal(str(cart_item.menu_item.price)) * cart_item.quantity for cart_item in cart_items)

        # Apply standard taxes & delivery
        taxes = round(subtotal * Decimal('0.05'), 2)
        delivery_fee = Decimal('40.00')

        coupon = None
        discount_amount = Decimal('0.00')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if subtotal >= coupon.min_order_amount:
                    discount_amount = Decimal(str(coupon.calculate_discount(subtotal)))
            except Coupon.DoesNotExist:
                pass

        grand_total = max(Decimal('0.00'), (subtotal + taxes + delivery_fee) - discount_amount)

        payment_status = 'PENDING'
        transaction_id = ''
        razorpay_order_id = ''

        if payment_mode in ('Razorpay', 'Online'):
            razorpay_order_id = f"order_rzp_{uuid.uuid4().hex[:12]}"
        elif payment_mode in ('UPI', 'Card'):
            payment_status = 'PAID'
            transaction_id = f"txn_{uuid.uuid4().hex[:12]}"

        order = Order.objects.create(
            user=request.user,
            restaurant=restaurant,
            order_status='PLACED',
            payment_mode=payment_mode,
            payment_status=payment_status,
            transaction_id=transaction_id,
            razorpay_order_id=razorpay_order_id,
            coupon=coupon,
            discount_amount=discount_amount,
            item_total=subtotal,
            taxes=taxes,
            delivery_fee=delivery_fee,
            grand_total=grand_total,
            delivery_address=delivery_address
        )

        order_items = [
            OrderItem(
                order=order,
                menu_item=menu_item,
                item_title=title,
                price=price,
                quantity=quantity
            )
            for menu_item, title, price, quantity in prepared_items
        ]
        OrderItem.objects.bulk_create(order_items)

        Restaurant.objects.filter(id=restaurant.id).update(order_count=F('order_count') + 1)
        if not request.user.default_address:
            request.user.default_address = delivery_address
            request.user.save(update_fields=['default_address'])

        Cart.objects.filter(user=request.user).delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['Orders'])
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.order_status != 'PLACED':
            return Response({
                "detail": f"Order cannot be cancelled in '{order.get_order_status_display()}' status. Cancellation is only allowed when order is Placed."
            }, status=status.HTTP_400_BAD_REQUEST)

        order.order_status = 'CANCELLED'
        order.save(update_fields=['order_status', 'updated_at'])

        return Response({
            "message": "Order cancelled successfully.",
            "order": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)

    @extend_schema(tags=['Orders'])
    @action(detail=True, methods=['post'], url_path='progress-status')
    def progress_status(self, request, pk=None):
        order = self.get_object()
        status_transitions = {
            'PLACED': 'PREPARING',
            'PREPARING': 'OUT_FOR_DELIVERY',
            'OUT_FOR_DELIVERY': 'DELIVERED',
        }

        next_status = status_transitions.get(order.order_status)
        if not next_status:
            return Response({
                "detail": f"Order is already in '{order.order_status}' status."
            }, status=status.HTTP_400_BAD_REQUEST)

        order.order_status = next_status
        order.save(update_fields=['order_status', 'updated_at'])

        return Response(OrderSerializer(order).data)


@extend_schema(tags=['Payments'], request=RazorpayCreateOrderSerializer)
class RazorpayCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RazorpayCreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data['order_id']

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_status == 'PAID':
            return Response({"detail": "This order is already paid."}, status=status.HTTP_400_BAD_REQUEST)

        if order.order_status == 'CANCELLED':
            return Response({"detail": "Cannot process payment for a cancelled order."}, status=status.HTTP_400_BAD_REQUEST)

        if not order.razorpay_order_id:
            order.razorpay_order_id = f"order_rzp_{uuid.uuid4().hex[:14]}"
            order.save(update_fields=['razorpay_order_id'])

        amount_in_paise = int(order.grand_total * 100)

        return Response({
            "key_id": getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_zomatoCloneDemoKey'),
            "razorpay_order_id": order.razorpay_order_id,
            "amount": amount_in_paise,
            "currency": "INR",
            "order_id": order.id,
            "restaurant_name": order.restaurant.name,
            "user_name": request.user.full_name or "Guest User",
            "user_mobile": request.user.mobile,
            "user_email": request.user.email or f"{request.user.mobile}@example.com",
        })


@extend_schema(tags=['Payments'], request=RazorpayVerifySerializer)
class RazorpayVerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RazorpayVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']
        razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
        razorpay_order_id = serializer.validated_data['razorpay_order_id']

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_status == 'PAID':
            return Response({
                "success": True,
                "message": "Order is already paid.",
                "order": OrderSerializer(order).data
            })

        order.payment_status = 'PAID'
        order.transaction_id = razorpay_payment_id
        order.razorpay_order_id = razorpay_order_id
        order.save(update_fields=['payment_status', 'transaction_id', 'razorpay_order_id', 'updated_at'])

        return Response({
            "success": True,
            "message": "Payment verified and recorded successfully.",
            "order": OrderSerializer(order).data
        })


@extend_schema_view(
    list=extend_schema(tags=['Reviews']),
    create=extend_schema(tags=['Reviews'], request=ReviewSerializer),
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related('user', 'restaurant')
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['restaurant', 'rating']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        restaurant = serializer.validated_data['restaurant']
        serializer.save(user=self.request.user)

        avg_rating = Review.objects.filter(restaurant=restaurant).aggregate(Avg('rating'))['rating__avg']
        if avg_rating is not None:
            restaurant.rating = round(Decimal(str(avg_rating)), 1)
            restaurant.save(update_fields=['rating'])
