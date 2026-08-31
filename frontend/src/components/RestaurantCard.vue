<script setup>
import { computed } from 'vue'

const props = defineProps({
  restaurant: {
    type: Object,
    required: true,
  },
})

// Color-coded rating logic
const ratingBadgeClass = computed(() => {
  const r = parseFloat(props.restaurant.rating)
  if (r >= 4.0) return 'bg-emerald-600 text-white'
  if (r >= 3.0) return 'bg-amber-500 text-white'
  return 'bg-red-500 text-white'
})

const defaultImage = 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&auto=format&fit=crop&q=80'

function handleImageError(event) {
  event.target.src = defaultImage
}
</script>

<template>
  <RouterLink
    :to="`/restaurant/${restaurant.id}`"
    class="group block bg-white rounded-3xl border border-gray-200/80 overflow-hidden shadow-card hover:shadow-card-hover hover:-translate-y-1.5 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-zomato-red flex flex-col justify-between"
  >
    <!-- Image Container (16:9) -->
    <div class="relative aspect-16/9 w-full bg-gray-100 overflow-hidden">
      <img
        :src="restaurant.image_url || defaultImage"
        :alt="restaurant.name"
        @error="handleImageError"
        class="w-full h-full object-cover group-hover:scale-106 transition-transform duration-500 ease-out"
        loading="lazy"
      />

      <!-- Gradient Overlay for Legibility -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/10 pointer-events-none"></div>

      <!-- Pure Veg Tag Overlay -->
      <div
        v-if="restaurant.is_pure_veg"
        class="absolute top-3 left-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-full text-[10px] font-extrabold text-veg-green shadow-xs flex items-center gap-1 tracking-wider"
      >
        <span>🌱</span>
        <span>PURE VEG</span>
      </div>

      <!-- Delivery Time Overlay -->
      <div class="absolute bottom-3 right-3 bg-black/70 backdrop-blur-md text-white px-2.5 py-1 rounded-xl text-xs font-bold flex items-center gap-1 shadow-xs">
        <span>⏱</span> {{ restaurant.delivery_time }} mins
      </div>

      <!-- Promoted / Offer Pill -->
      <div class="absolute bottom-3 left-3 text-white text-xs font-extrabold tracking-wide drop-shadow-md">
        <span class="text-amber-300 font-extrabold">50% OFF</span> up to ₹100
      </div>
    </div>

    <!-- Details Body -->
    <div class="p-5 flex-1 flex flex-col justify-between space-y-3">
      <div>
        <!-- Title & Rating -->
        <div class="flex items-start justify-between gap-2 mb-1">
          <h3 class="text-base font-extrabold text-surface-dark group-hover:text-zomato-red transition-colors truncate">
            {{ restaurant.name }}
          </h3>
          <span
            :class="[ratingBadgeClass, 'inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs font-extrabold shrink-0 shadow-xs']"
          >
            <span>{{ parseFloat(restaurant.rating).toFixed(1) }}</span>
            <span class="text-[10px]">★</span>
          </span>
        </div>

        <!-- Cuisine & Cost for Two -->
        <div class="flex items-center justify-between text-xs text-surface-muted">
          <span class="truncate font-medium">{{ restaurant.cuisine }}</span>
          <span class="font-bold text-surface-dark shrink-0">₹{{ restaurant.avg_cost_for_two }} for two</span>
        </div>
      </div>

      <!-- Address & Order Count -->
      <div class="pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
        <span class="truncate max-w-[180px]">📍 {{ restaurant.address || restaurant.city }}</span>
        <span v-if="restaurant.order_count > 0" class="text-[11px] text-gray-500 font-semibold shrink-0 bg-gray-50 px-2 py-0.5 rounded-md border border-gray-100">
          {{ restaurant.order_count }}+ orders
        </span>
      </div>
    </div>
  </RouterLink>
</template>
