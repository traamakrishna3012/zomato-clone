import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const cartItems = ref(JSON.parse(localStorage.getItem('cart_items') || '[]'))
  const activeRestaurant = ref(JSON.parse(localStorage.getItem('cart_restaurant') || 'null'))
  const appliedCoupon = ref(JSON.parse(localStorage.getItem('cart_coupon') || 'null'))
  const isDrawerOpen = ref(false)
  const showMismatchModal = ref(false)
  const pendingItem = ref(null)

  const activeRestaurantId = computed(() => activeRestaurant.value?.id || null)
  const activeRestaurantName = computed(() => activeRestaurant.value?.name || '')

  const itemCount = computed(() => {
    return cartItems.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const itemTotal = computed(() => {
    return cartItems.value.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0)
  })

  // 5% GST on food items
  const taxes = computed(() => {
    return Math.round(itemTotal.value * 0.05 * 100) / 100
  })

  // ₹40 standard delivery fee (free if empty)
  const deliveryFee = computed(() => {
    return cartItems.value.length > 0 ? 40 : 0
  })

  const discountAmount = computed(() => {
    if (!appliedCoupon.value) return 0
    return parseFloat(appliedCoupon.value.discount_amount || 0)
  })

  const grandTotal = computed(() => {
    const total = itemTotal.value + taxes.value + deliveryFee.value - discountAmount.value
    return Math.max(0, Math.round(total * 100) / 100)
  })

  function saveToStorage() {
    localStorage.setItem('cart_items', JSON.stringify(cartItems.value))
    localStorage.setItem('cart_restaurant', JSON.stringify(activeRestaurant.value))
    localStorage.setItem('cart_coupon', JSON.stringify(appliedCoupon.value))
  }

  function getItemQuantity(itemId) {
    const item = cartItems.value.find((ci) => ci.id === itemId)
    return item ? item.quantity : 0
  }

  function addToCart(item, restaurant) {
    // Cross-restaurant conflict check
    if (activeRestaurantId.value && activeRestaurantId.value !== restaurant.id) {
      pendingItem.value = { item, restaurant }
      showMismatchModal.value = true
      return
    }

    if (!activeRestaurant.value) {
      activeRestaurant.value = {
        id: restaurant.id,
        name: restaurant.name,
        image_url: restaurant.image_url,
        city: restaurant.city,
      }
    }

    const existing = cartItems.value.find((ci) => ci.id === item.id)
    if (existing) {
      existing.quantity += 1
    } else {
      cartItems.value.push({
        id: item.id,
        title: item.title,
        price: parseFloat(item.price),
        image_url: item.image_url,
        is_veg: item.is_veg,
        category: item.category,
        quantity: 1,
      })
    }

    saveToStorage()
  }

  function updateQuantity(itemId, quantity) {
    const index = cartItems.value.findIndex((ci) => ci.id === itemId)
    if (index === -1) return

    if (quantity <= 0) {
      cartItems.value.splice(index, 1)
      if (cartItems.value.length === 0) {
        activeRestaurant.value = null
        appliedCoupon.value = null
      }
    } else {
      cartItems.value[index].quantity = quantity
    }

    saveToStorage()
  }

  function applyCoupon(couponData) {
    appliedCoupon.value = couponData
    saveToStorage()
  }

  function removeCoupon() {
    appliedCoupon.value = null
    saveToStorage()
  }

  function clearCart() {
    cartItems.value = []
    activeRestaurant.value = null
    appliedCoupon.value = null
    saveToStorage()
  }

  function confirmRestaurantSwitch() {
    if (!pendingItem.value) return
    clearCart()
    addToCart(pendingItem.value.item, pendingItem.value.restaurant)
    pendingItem.value = null
    showMismatchModal.value = false
  }

  function cancelRestaurantSwitch() {
    pendingItem.value = null
    showMismatchModal.value = false
  }

  function openDrawer() {
    isDrawerOpen.value = true
  }

  function closeDrawer() {
    isDrawerOpen.value = false
  }

  return {
    cartItems,
    activeRestaurant,
    activeRestaurantId,
    activeRestaurantName,
    appliedCoupon,
    discountAmount,
    isDrawerOpen,
    showMismatchModal,
    pendingItem,
    itemCount,
    itemTotal,
    taxes,
    deliveryFee,
    grandTotal,
    getItemQuantity,
    addToCart,
    updateQuantity,
    applyCoupon,
    removeCoupon,
    clearCart,
    confirmRestaurantSwitch,
    cancelRestaurantSwitch,
    openDrawer,
    closeDrawer,
  }
})
