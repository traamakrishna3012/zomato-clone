<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import RazorpayModal from '../components/RazorpayModal.vue'
import api from '../services/api'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const deliveryAddress = ref('')
const paymentMode = ref('Razorpay')
const isSubmitting = ref(false)
const errorMessage = ref('')
const couponInput = ref('')
const couponMessage = ref('')
const couponError = ref('')
const isApplyingCoupon = ref(false)
const availableCoupons = ref([])

// Razorpay state
const showRazorpayModal = ref(false)
const pendingOrder = ref(null)

const paymentOptions = [
  { id: 'Razorpay', label: 'Razorpay Payment Gateway (Test Mode)', icon: '⚡', desc: 'UPI, Credit/Debit Cards, Netbanking & Wallets' },
  { id: 'COD', label: 'Cash on Delivery (COD)', icon: '💵', desc: 'Pay with cash at your doorstep upon delivery' },
  { id: 'UPI', label: 'Instant UPI Transfer', icon: '📱', desc: 'Direct UPI payment without gateway step' },
]

async function fetchCoupons() {
  try {
    const res = await api.get('/coupons/')
    availableCoupons.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load coupons', err)
  }
}

async function handleApplyCoupon(codeToApply = null) {
  const code = (codeToApply || couponInput.value).trim().toUpperCase()
  if (!code) return

  couponError.value = ''
  couponMessage.value = ''
  isApplyingCoupon.value = true

  try {
    const res = await api.post('/coupons/apply/', {
      code,
      item_total: cartStore.itemTotal,
    })

    cartStore.applyCoupon({
      code: res.data.code,
      description: res.data.description,
      discount_amount: res.data.discount_amount,
    })

    couponMessage.value = res.data.message
    couponInput.value = ''
  } catch (err) {
    couponError.value = err.response?.data?.detail || 'Invalid coupon code or minimum order condition not met.'
  } finally {
    isApplyingCoupon.value = false
  }
}

function handleRemoveCoupon() {
  cartStore.removeCoupon()
  couponMessage.value = ''
  couponError.value = ''
}

async function handlePlaceOrder() {
  errorMessage.value = ''
  
  if (!authStore.isAuthenticated) {
    authStore.openAuthModal('mobile')
    return
  }

  if (!deliveryAddress.value.trim()) {
    errorMessage.value = 'Please provide a valid delivery address.'
    return
  }

  if (cartStore.cartItems.length === 0) {
    errorMessage.value = 'Your cart is empty.'
    return
  }

  isSubmitting.value = true

  try {
    const payload = {
      delivery_address: deliveryAddress.value.trim(),
      payment_mode: paymentMode.value,
      coupon_code: cartStore.appliedCoupon ? cartStore.appliedCoupon.code : '',
      items: cartStore.cartItems.map((ci) => ({
        menu_item_id: ci.id,
        quantity: ci.quantity,
      })),
    }

    const response = await api.post('/orders/', payload)
    const newOrder = response.data

    if (paymentMode.value === 'Razorpay') {
      // Open Razorpay test modal
      pendingOrder.value = newOrder
      showRazorpayModal.value = true
      isSubmitting.value = false
    } else {
      // Immediate order completion
      cartStore.clearCart()
      router.push({ name: 'orders' })
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Failed to place order. Please try again.'
    isSubmitting.value = false
  }
}

function handleRazorpaySuccess(verifiedOrder) {
  showRazorpayModal.value = false
  cartStore.clearCart()
  router.push({ name: 'orders' })
}

function handleRazorpayClose() {
  showRazorpayModal.value = false
  cartStore.clearCart()
  router.push({ name: 'orders' })
}

onMounted(() => {
  fetchCoupons()
  if (authStore.user?.default_address) {
    deliveryAddress.value = authStore.user.default_address
  } else {
    deliveryAddress.value = 'Flat 402, Sunshine Heights, Indore'
  }
})
</script>

<template>
  <div class="max-w-5xl mx-auto py-6">
    <div class="mb-6">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-surface-dark tracking-tight">
        Checkout & Payment
      </h1>
      <p class="text-xs sm:text-sm text-surface-muted">
        Confirm delivery address, apply promo discounts, and choose payment method.
      </p>
    </div>

    <!-- Empty Cart Alert -->
    <div
      v-if="cartStore.cartItems.length === 0"
      class="text-center py-16 bg-white rounded-3xl border border-card-border p-8 space-y-4 shadow-xs"
    >
      <div class="text-5xl">🛍️</div>
      <h2 class="text-xl font-bold text-surface-dark">
        Your cart is currently empty
      </h2>
      <p class="text-sm text-surface-muted max-w-sm mx-auto">
        Browse restaurants and add delicious dishes to begin checkout.
      </p>
      <RouterLink
        to="/"
        class="inline-block px-6 py-3 bg-zomato-red hover:bg-zomato-red-dark text-white font-bold rounded-2xl text-xs uppercase tracking-wider transition"
      >
        Explore Restaurants
      </RouterLink>
    </div>

    <!-- Checkout Grid -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- Left Column: Address, Coupons & Payment Mode -->
      <div class="lg:col-span-7 space-y-6">
        
        <!-- Delivery Address Box -->
        <div class="bg-white rounded-3xl border border-card-border p-6 shadow-xs space-y-4">
          <div class="flex items-center gap-3">
            <span class="text-xl">📍</span>
            <div>
              <h3 class="text-base font-bold text-surface-dark">
                Delivery Address
              </h3>
              <p class="text-xs text-surface-muted">
                Where should we deliver your order?
              </p>
            </div>
          </div>

          <textarea
            v-model="deliveryAddress"
            rows="3"
            placeholder="Enter complete delivery address (House/Flat No, Landmark, City)..."
            class="w-full px-4 py-3 rounded-2xl border border-card-border bg-gray-50 focus:bg-white text-sm focus:border-zomato-red focus:outline-none transition"
            required
          ></textarea>
        </div>

        <!-- Coupons & Promo Codes Section -->
        <div class="bg-white rounded-3xl border border-card-border p-6 shadow-xs space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-xl">🏷️</span>
              <div>
                <h3 class="text-base font-bold text-surface-dark">
                  Coupons & Offers
                </h3>
                <p class="text-xs text-surface-muted">
                  Apply promo code for extra savings
                </p>
              </div>
            </div>

            <span
              v-if="cartStore.appliedCoupon"
              class="px-2.5 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-xl flex items-center gap-1"
            >
              ✓ Applied
            </span>
          </div>

          <!-- Applied Coupon Card -->
          <div
            v-if="cartStore.appliedCoupon"
            class="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center justify-between"
          >
            <div>
              <div class="flex items-center gap-2">
                <span class="font-extrabold text-emerald-800 text-sm tracking-wider">
                  {{ cartStore.appliedCoupon.code }}
                </span>
                <span class="text-xs text-emerald-600 font-semibold">
                  (Saved ₹{{ cartStore.discountAmount.toFixed(2) }})
                </span>
              </div>
              <p class="text-xs text-emerald-700 mt-0.5">
                {{ cartStore.appliedCoupon.description }}
              </p>
            </div>

            <button
              type="button"
              @click="handleRemoveCoupon"
              class="text-xs font-bold text-red-600 hover:text-red-800 transition cursor-pointer px-2 py-1"
            >
              Remove
            </button>
          </div>

          <!-- Coupon Input Form -->
          <div v-else class="flex gap-2">
            <input
              v-model="couponInput"
              type="text"
              placeholder="ENTER PROMO CODE"
              class="flex-1 px-4 py-2.5 rounded-2xl border border-card-border bg-gray-50 uppercase text-xs font-bold tracking-wider focus:bg-white focus:border-zomato-red focus:outline-none transition"
              @keyup.enter="handleApplyCoupon()"
            />
            <button
              type="button"
              @click="handleApplyCoupon()"
              :disabled="isApplyingCoupon || !couponInput.trim()"
              class="px-5 py-2.5 bg-zomato-red hover:bg-zomato-red-dark text-white font-extrabold rounded-2xl text-xs uppercase tracking-wider transition cursor-pointer disabled:opacity-50"
            >
              {{ isApplyingCoupon ? '...' : 'Apply' }}
            </button>
          </div>

          <!-- Coupon Feedback Alerts -->
          <div v-if="couponError" class="text-xs text-zomato-red font-medium">
            {{ couponError }}
          </div>
          <div v-if="couponMessage" class="text-xs text-emerald-700 font-medium">
            {{ couponMessage }}
          </div>

          <!-- Available Coupons Carousel -->
          <div v-if="!cartStore.appliedCoupon && availableCoupons.length > 0" class="pt-2 space-y-2">
            <p class="text-[11px] font-bold text-surface-muted uppercase tracking-wider">
              Available Promo Codes
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div
                v-for="c in availableCoupons"
                :key="c.id"
                class="p-3 border border-dashed border-gray-300 hover:border-zomato-red rounded-2xl bg-gray-50/70 hover:bg-red-50/30 transition flex flex-col justify-between"
              >
                <div>
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-extrabold text-surface-dark tracking-wider">
                      {{ c.code }}
                    </span>
                    <button
                      type="button"
                      @click="handleApplyCoupon(c.code)"
                      class="text-[11px] font-bold text-zomato-red hover:underline cursor-pointer"
                    >
                      APPLY
                    </button>
                  </div>
                  <p class="text-[11px] text-surface-muted mt-1">
                    {{ c.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Payment Mode Selector -->
        <div class="bg-white rounded-3xl border border-card-border p-6 shadow-xs space-y-4">
          <div class="flex items-center gap-3">
            <span class="text-xl">💳</span>
            <div>
              <h3 class="text-base font-bold text-surface-dark">
                Select Payment Mode
              </h3>
              <p class="text-xs text-surface-muted">
                Choose your preferred payment method
              </p>
            </div>
          </div>

          <div class="space-y-3">
            <label
              v-for="opt in paymentOptions"
              :key="opt.id"
              :class="[
                'flex items-center justify-between p-4 rounded-2xl border transition cursor-pointer',
                paymentMode === opt.id
                  ? 'border-zomato-red bg-red-50/40 ring-1 ring-zomato-red shadow-xs'
                  : 'border-card-border hover:bg-gray-50'
              ]"
            >
              <div class="flex items-center gap-3.5">
                <span class="text-2xl">{{ opt.icon }}</span>
                <div>
                  <div class="text-sm font-bold text-surface-dark flex items-center gap-2">
                    <span>{{ opt.label }}</span>
                    <span v-if="opt.id === 'Razorpay'" class="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-extrabold rounded-md">
                      FAST
                    </span>
                  </div>
                  <div class="text-xs text-surface-muted">
                    {{ opt.desc }}
                  </div>
                </div>
              </div>

              <input
                type="radio"
                name="payment_mode"
                :value="opt.id"
                v-model="paymentMode"
                class="accent-zomato-red w-4 h-4 cursor-pointer"
              />
            </label>
          </div>
        </div>

        <!-- Error Message -->
        <div
          v-if="errorMessage"
          class="p-4 bg-red-50 border border-red-200 text-zomato-red rounded-2xl text-sm font-medium"
        >
          {{ errorMessage }}
        </div>
      </div>

      <!-- Right Column: Order Summary & Placement -->
      <div class="lg:col-span-5 space-y-6">
        <div class="bg-white rounded-3xl border border-card-border p-6 shadow-xs space-y-5 sticky top-24">
          
          <div>
            <h3 class="text-base font-bold text-surface-dark">
              Order Summary
            </h3>
            <p v-if="cartStore.activeRestaurantName" class="text-xs text-surface-muted truncate">
              From {{ cartStore.activeRestaurantName }}
            </p>
          </div>

          <!-- Items Breakdown -->
          <div class="space-y-3 max-h-56 overflow-y-auto divide-y divide-card-border pr-1">
            <div
              v-for="item in cartStore.cartItems"
              :key="item.id"
              class="flex items-center justify-between gap-3 pt-3 first:pt-0"
            >
              <div class="flex items-center gap-2 truncate">
                <span
                  v-if="item.is_veg"
                  class="w-3 h-3 border border-veg-green rounded-xs flex items-center justify-center p-0.5 shrink-0"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-veg-green block"></span>
                </span>
                <span
                  v-else
                  class="w-3 h-3 border border-zomato-red rounded-xs flex items-center justify-center p-0.5 shrink-0"
                >
                  <span class="w-0 h-0 border-l-[2.5px] border-l-transparent border-r-[2.5px] border-r-transparent border-b-[4px] border-b-zomato-red block"></span>
                </span>
                <span class="text-xs font-semibold text-surface-dark truncate">
                  {{ item.title }}
                </span>
                <span class="text-xs text-surface-muted shrink-0">
                  × {{ item.quantity }}
                </span>
              </div>

              <span class="text-xs font-bold text-surface-dark shrink-0">
                ₹{{ (item.price * item.quantity).toFixed(0) }}
              </span>
            </div>
          </div>

          <!-- Bill Details Table -->
          <div class="pt-4 border-t border-card-border space-y-2.5 text-xs text-surface-muted">
            <div class="flex items-center justify-between">
              <span>Item Total</span>
              <span class="font-medium text-surface-dark">₹{{ cartStore.itemTotal.toFixed(2) }}</span>
            </div>

            <div class="flex items-center justify-between">
              <span>Delivery Partner Fee</span>
              <span class="font-medium text-surface-dark">₹{{ cartStore.deliveryFee.toFixed(2) }}</span>
            </div>

            <div class="flex items-center justify-between">
              <span>Taxes & Restaurant Charges (5% GST)</span>
              <span class="font-medium text-surface-dark">₹{{ cartStore.taxes.toFixed(2) }}</span>
            </div>

            <!-- Discount Row -->
            <div
              v-if="cartStore.discountAmount > 0"
              class="flex items-center justify-between text-emerald-600 font-bold bg-emerald-50 px-2.5 py-1.5 rounded-xl border border-emerald-100"
            >
              <span>Coupon Discount ({{ cartStore.appliedCoupon?.code }})</span>
              <span>- ₹{{ cartStore.discountAmount.toFixed(2) }}</span>
            </div>

            <div class="pt-3 border-t border-card-border flex items-center justify-between text-base font-extrabold text-surface-dark">
              <span>To Pay</span>
              <span class="text-zomato-red text-lg">₹{{ cartStore.grandTotal.toFixed(2) }}</span>
            </div>
          </div>

          <!-- Place Order Button -->
          <button
            type="button"
            @click="handlePlaceOrder"
            :disabled="isSubmitting"
            class="w-full py-4 bg-zomato-red hover:bg-zomato-red-dark text-white font-extrabold rounded-2xl shadow-sm transition flex items-center justify-center gap-2 text-sm uppercase tracking-wider disabled:opacity-50 cursor-pointer hover:scale-[1.01] active:scale-[0.99]"
          >
            <span v-if="isSubmitting" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>
              {{ paymentMode === 'Razorpay' ? 'Proceed to Razorpay' : 'Place Order' }} • ₹{{ cartStore.grandTotal.toFixed(0) }}
            </span>
          </button>

          <p class="text-[11px] text-center text-surface-muted flex items-center justify-center gap-1.5">
            <span>🔒</span> Safe & secure payment powered by Razorpay Test Gateway
          </p>
        </div>
      </div>

    </div>

    <!-- Razorpay Payment Gateway Modal -->
    <RazorpayModal
      :is-open="showRazorpayModal"
      :order="pendingOrder"
      @success="handleRazorpaySuccess"
      @close="handleRazorpayClose"
    />
  </div>
</template>
