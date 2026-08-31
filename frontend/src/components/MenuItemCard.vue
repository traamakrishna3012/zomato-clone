<script setup>
import { computed } from 'vue'
import { useCartStore } from '../stores/cart'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  restaurant: {
    type: Object,
    required: true,
  },
})

const cartStore = useCartStore()

const currentQuantity = computed(() => {
  return cartStore.getItemQuantity(props.item.id)
})

function handleAdd() {
  cartStore.addToCart(props.item, props.restaurant)
}

function handleIncrement() {
  cartStore.updateQuantity(props.item.id, currentQuantity.value + 1)
}

function handleDecrement() {
  cartStore.updateQuantity(props.item.id, currentQuantity.value - 1)
}

const defaultDishImage = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&auto=format&fit=crop&q=80'

function handleImageError(event) {
  event.target.src = defaultDishImage
}
</script>

<template>
  <div class="flex items-start justify-between gap-6 py-6 border-b border-gray-100 last:border-b-0 hover:bg-gray-50/70 p-4 rounded-3xl transition-colors duration-200">
    
    <!-- Left Column: Veg/Non-veg icon, Title, Price, Description -->
    <div class="flex-1 pr-2 space-y-1.5">
      <!-- Veg / Non-Veg Icon & Bestseller Badge -->
      <div class="flex items-center gap-2 mb-1">
        <!-- Veg Icon -->
        <span
          v-if="item.is_veg"
          class="w-4 h-4 border border-veg-green rounded-xs flex items-center justify-center p-0.5 shrink-0"
          title="Pure Vegetarian"
        >
          <span class="w-2 h-2 rounded-full bg-veg-green block"></span>
        </span>

        <!-- Non-Veg Icon -->
        <span
          v-else
          class="w-4 h-4 border border-zomato-red rounded-xs flex items-center justify-center p-0.5 shrink-0"
          title="Non-Vegetarian"
        >
          <span class="w-0 h-0 border-l-[3.5px] border-l-transparent border-r-[3.5px] border-r-transparent border-b-[6px] border-b-zomato-red block"></span>
        </span>

        <!-- Bestseller Tag -->
        <span
          v-if="item.is_bestseller"
          class="inline-flex items-center gap-1 px-2.5 py-0.5 bg-amber-100 text-amber-900 rounded-lg text-[10px] font-extrabold uppercase tracking-wide"
        >
          <span>★</span>
          <span>Bestseller</span>
        </span>
      </div>

      <!-- Item Title -->
      <h4 class="text-base sm:text-lg font-extrabold text-surface-dark tracking-tight leading-snug">
        {{ item.title }}
      </h4>

      <!-- Price -->
      <div class="text-sm sm:text-base font-extrabold text-surface-dark">
        ₹{{ parseFloat(item.price).toFixed(0) }}
      </div>

      <!-- Description -->
      <p v-if="item.description" class="text-xs text-surface-muted leading-relaxed line-clamp-2 max-w-lg">
        {{ item.description }}
      </p>
    </div>

    <!-- Right Column: Image & Add / Quantity Button -->
    <div class="relative shrink-0 flex flex-col items-center">
      <div class="w-32 h-28 sm:w-36 sm:h-32 rounded-3xl bg-gray-100 overflow-hidden shadow-2xs border border-gray-200/80">
        <img
          :src="item.image_url || defaultDishImage"
          :alt="item.title"
          @error="handleImageError"
          class="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
      </div>

      <!-- ADD Button / Active Quantity Counter -->
      <div class="absolute -bottom-3 shadow-md">
        <!-- Not in Cart: Single ADD Button -->
        <button
          v-if="currentQuantity === 0"
          type="button"
          @click="handleAdd"
          class="px-7 py-2 bg-white hover:bg-red-50/50 text-zomato-red font-extrabold text-xs rounded-2xl border border-red-200 shadow-sm uppercase tracking-wider transition hover:scale-105 active:scale-95 cursor-pointer"
        >
          ADD
        </button>

        <!-- In Cart: (- QTY +) Counter -->
        <div
          v-else
          class="flex items-center bg-zomato-red text-white rounded-2xl shadow-sm overflow-hidden"
        >
          <button
            type="button"
            @click="handleDecrement"
            class="px-3 py-1.5 text-sm font-bold hover:bg-zomato-red-dark transition cursor-pointer active:scale-90"
          >
            −
          </button>
          <span class="px-2.5 py-1 text-xs font-extrabold min-w-[24px] text-center">
            {{ currentQuantity }}
          </span>
          <button
            type="button"
            @click="handleIncrement"
            class="px-3 py-1.5 text-sm font-bold hover:bg-zomato-red-dark transition cursor-pointer active:scale-90"
          >
            +
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
