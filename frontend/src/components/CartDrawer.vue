<script setup>
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'

const router = useRouter()
const cartStore = useCartStore()

function handleCheckout() {
  cartStore.closeDrawer()
  router.push({ name: 'checkout' })
}
</script>

<template>
  <div>
    <!-- Backdrop Overlay -->
    <div
      v-if="cartStore.isDrawerOpen"
      class="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs transition-opacity"
      @click="cartStore.closeDrawer"
    ></div>

    <!-- Drawer Panel -->
    <div
      :class="[
        'fixed top-0 right-0 bottom-0 w-full sm:w-96 bg-white z-50 shadow-2xl flex flex-col transition-transform duration-300 ease-in-out',
        cartStore.isDrawerOpen ? 'translate-x-0' : 'translate-x-full'
      ]"
    >
      <!-- Header -->
      <div class="p-4 sm:p-5 border-b border-card-border flex items-center justify-between">
        <div>
          <h3 class="text-lg font-bold text-surface-dark">
            My Cart
          </h3>
          <p v-if="cartStore.activeRestaurantName" class="text-xs text-surface-muted truncate">
            From {{ cartStore.activeRestaurantName }}
          </p>
        </div>
        <button
          type="button"
          @click="cartStore.closeDrawer"
          class="p-2 text-surface-muted hover:text-surface-dark hover:bg-gray-100 rounded-full transition cursor-pointer"
        >
          ✕
        </button>
      </div>

      <!-- Drawer Body -->
      <div class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-5">
        <!-- Empty Cart State -->
        <div v-if="cartStore.cartItems.length === 0" class="text-center py-16 text-surface-muted space-y-3">
          <div class="text-4xl">🛒</div>
          <p class="text-sm font-semibold text-surface-dark">Your cart is empty</p>
          <p class="text-xs text-surface-muted">Add tasty dishes from restaurants to get started!</p>
        </div>

        <!-- Cart Items List -->
        <div v-else class="space-y-3">
          <div
            v-for="item in cartStore.cartItems"
            :key="item.id"
            class="flex items-center justify-between gap-3 p-3 bg-gray-50 rounded-2xl border border-card-border"
          >
            <div class="flex items-center gap-2.5 min-w-0">
              <!-- Veg / Non-veg dot -->
              <span
                v-if="item.is_veg"
                class="w-3.5 h-3.5 border border-veg-green rounded-xs flex items-center justify-center p-0.5 shrink-0"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-veg-green block"></span>
              </span>
              <span
                v-else
                class="w-3.5 h-3.5 border border-zomato-red rounded-xs flex items-center justify-center p-0.5 shrink-0"
              >
                <span class="w-0 h-0 border-l-[3px] border-l-transparent border-r-[3px] border-r-transparent border-b-[5px] border-b-zomato-red block"></span>
              </span>

              <div class="truncate">
                <div class="text-xs font-bold text-surface-dark truncate">
                  {{ item.title }}
                </div>
                <div class="text-[11px] text-surface-muted">
                  ₹{{ item.price }} each
                </div>
              </div>
            </div>

            <!-- Quantity Counter & Total -->
            <div class="flex items-center gap-3 shrink-0">
              <div class="flex items-center bg-white border border-card-border rounded-xl shadow-xs overflow-hidden">
                <button
                  type="button"
                  @click="cartStore.updateQuantity(item.id, item.quantity - 1)"
                  class="px-2 py-0.5 text-xs font-bold text-zomato-red hover:bg-gray-50 transition cursor-pointer"
                >
                  −
                </button>
                <span class="px-1.5 text-xs font-bold min-w-[16px] text-center">
                  {{ item.quantity }}
                </span>
                <button
                  type="button"
                  @click="cartStore.updateQuantity(item.id, item.quantity + 1)"
                  class="px-2 py-0.5 text-xs font-bold text-zomato-red hover:bg-gray-50 transition cursor-pointer"
                >
                  +
                </button>
              </div>

              <div class="text-xs font-bold text-surface-dark min-w-[50px] text-right">
                ₹{{ (item.price * item.quantity).toFixed(0) }}
              </div>
            </div>
          </div>

          <!-- Bill Details Card -->
          <div class="p-4 bg-gray-50 rounded-2xl border border-card-border space-y-2 text-xs">
            <h4 class="font-bold text-surface-dark text-xs uppercase tracking-wider mb-2">
              Bill Details
            </h4>
            
            <div class="flex items-center justify-between text-surface-muted">
              <span>Item Total</span>
              <span class="font-medium text-surface-dark">₹{{ cartStore.itemTotal.toFixed(2) }}</span>
            </div>

            <div class="flex items-center justify-between text-surface-muted">
              <span>Delivery Fee</span>
              <span class="font-medium text-surface-dark">₹{{ cartStore.deliveryFee.toFixed(2) }}</span>
            </div>

            <div class="flex items-center justify-between text-surface-muted">
              <span>Taxes & Charges (5% GST)</span>
              <span class="font-medium text-surface-dark">₹{{ cartStore.taxes.toFixed(2) }}</span>
            </div>

            <div class="pt-2 border-t border-card-border flex items-center justify-between text-sm font-extrabold text-surface-dark">
              <span>Grand Total</span>
              <span class="text-zomato-red">₹{{ cartStore.grandTotal.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Fixed CTA -->
      <div v-if="cartStore.cartItems.length > 0" class="p-4 sm:p-5 border-t border-card-border bg-white">
        <button
          type="button"
          @click="handleCheckout"
          class="w-full py-3.5 bg-zomato-red hover:bg-zomato-red-dark text-white font-bold rounded-2xl shadow-sm transition flex items-center justify-between px-5 text-sm cursor-pointer hover:scale-[1.01] active:scale-[0.99]"
        >
          <span>₹{{ cartStore.grandTotal.toFixed(0) }} Total</span>
          <span class="flex items-center gap-1">
            <span>Proceed to Checkout</span>
            <span>→</span>
          </span>
        </button>
      </div>
    </div>
  </div>
</template>
