from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification, Restaurant, MenuItem, Cart, Order, OrderItem, Review


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('mobile', 'full_name', 'email', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('mobile', 'full_name', 'email')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'default_address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'full_name', 'email', 'default_address'),
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'otp', 'is_verified', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('mobile',)


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine', 'city', 'rating', 'avg_cost_for_two', 'delivery_time', 'is_pure_veg', 'is_open', 'order_count')
    list_filter = ('city', 'is_pure_veg', 'is_open', 'cuisine')
    search_fields = ('name', 'cuisine', 'city')
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'restaurant', 'category', 'price', 'is_veg', 'is_bestseller', 'is_available')
    list_filter = ('category', 'is_veg', 'is_bestseller', 'is_available', 'restaurant__city')
    search_fields = ('title', 'restaurant__name')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'menu_item', 'quantity', 'created_at')
    search_fields = ('user__mobile', 'restaurant__name', 'menu_item__title')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_title', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'order_status', 'payment_mode', 'grand_total', 'created_at')
    list_filter = ('order_status', 'payment_mode', 'created_at')
    search_fields = ('user__mobile', 'restaurant__name', 'id')
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('restaurant__name', 'user__mobile', 'comment')
