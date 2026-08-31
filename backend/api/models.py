from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError("The Mobile number is required")
        user = self.model(mobile=mobile, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(mobile, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    mobile = models.CharField(max_length=15, unique=True, db_index=True)
    full_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True, null=True)
    default_address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.full_name or self.mobile


class OTPVerification(models.Model):
    mobile = models.CharField(max_length=15, db_index=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mobile} - {self.otp}"


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cuisine = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.0)
    avg_cost_for_two = models.PositiveIntegerField(default=500)
    is_pure_veg = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    image_url = models.URLField(max_length=500, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, default='Indore', db_index=True)
    delivery_time = models.PositiveIntegerField(default=30, help_text="Estimated delivery time in minutes")
    order_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating', '-order_count']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Starters', 'Starters'),
        ('Main Course', 'Main Course'),
        ('Desserts', 'Desserts'),
        ('Beverages', 'Beverages'),
    ]

    restaurant = models.ForeignKey(Restaurant, related_name='menu_items', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Main Course')
    is_veg = models.BooleanField(default=True)
    image_url = models.URLField(max_length=500, blank=True)
    is_bestseller = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'title']

    def __str__(self):
        return f"{self.title} ({self.restaurant.name})"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cart_items', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'menu_item')

    def __str__(self):
        return f"{self.user} - {self.menu_item.title} ({self.quantity})"


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENT', 'Percentage'),
        ('FLAT', 'Flat Amount'),
    ]

    code = models.CharField(max_length=30, unique=True, db_index=True)
    description = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='PERCENT')
    discount_value = models.DecimalField(max_digits=6, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    max_discount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def calculate_discount(self, subtotal):
        if subtotal < self.min_order_amount:
            return Decimal('0.00')

        if self.discount_type == 'PERCENT':
            discount = (subtotal * self.discount_value) / Decimal('100.0')
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return round(discount, 2)

        return round(min(self.discount_value, subtotal), 2)


class Order(models.Model):
    STATUS_CHOICES = [
        ('PLACED', 'Placed'),
        ('PREPARING', 'Preparing'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Razorpay', 'Razorpay'),
        ('Online', 'Online'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='orders', on_delete=models.CASCADE)
    order_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PLACED')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True)

    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    item_total = models.DecimalField(max_digits=10, decimal_places=2)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=40.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.restaurant.name} ({self.order_status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    item_title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item_title} x {self.quantity}"


class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.restaurant.name} ({self.rating}/5)"
