<script setup>
import { useCartStore } from '../stores/cart'

const cartStore = useCartStore()
</script>

<template>
  <div
    v-if="cartStore.showMismatchModal"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs transition-opacity"
    @click.self="cartStore.cancelRestaurantSwitch"
  >
    <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
      
      <div class="w-12 h-12 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center text-xl mb-4">
        ⚠️
      </div>

      <h3 class="text-xl font-bold text-surface-dark mb-2">
        Replace cart items?
      </h3>

      <p class="text-sm text-surface-muted leading-relaxed mb-6">
        Your cart already contains items from <span class="font-bold text-surface-dark">{{ cartStore.activeRestaurantName }}</span>. Would you like to reset your cart to add items from <span class="font-bold text-surface-dark">{{ cartStore.pendingItem?.restaurant?.name }}</span>?
      </p>

      <div class="flex items-center justify-end gap-3">
        <button
          type="button"
          @click="cartStore.cancelRestaurantSwitch"
          class="px-4 py-2.5 rounded-xl border border-card-border text-sm font-semibold text-surface-dark hover:bg-gray-50 transition cursor-pointer"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="cartStore.confirmRestaurantSwitch"
          class="px-5 py-2.5 rounded-xl bg-zomato-red hover:bg-zomato-red-dark text-white text-sm font-semibold shadow-xs transition cursor-pointer"
        >
          Yes, Reset Cart
        </button>
      </div>

    </div>
  </div>
</template>
