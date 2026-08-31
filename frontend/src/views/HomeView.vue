<script setup>
import { ref, onMounted } from 'vue'
import { useRestaurantStore } from '../stores/restaurant'
import RestaurantCard from '../components/RestaurantCard.vue'
import FilterSidebar from '../components/FilterSidebar.vue'

const restaurantStore = useRestaurantStore()
const copiedCoupon = ref('')

const featuredOffers = [
  { code: 'ZOMATO50', text: '50% OFF up to ₹100', min: 'Above ₹199' },
  { code: 'WELCOME100', text: 'Flat ₹100 OFF', min: 'Above ₹299' },
  { code: 'HUNGRY20', text: '20% OFF up to ₹150', min: 'Above ₹250' },
  { code: 'FEAST30', text: '30% OFF up to ₹200', min: 'Above ₹499' },
]

function copyCode(code) {
  navigator.clipboard?.writeText(code)
  copiedCoupon.value = code
  setTimeout(() => {
    copiedCoupon.value = ''
  }, 2000)
}

onMounted(() => {
  restaurantStore.fetchRestaurants()
  restaurantStore.fetchTopPicks()
})
</script>

<template>
  <div class="space-y-12 pb-12">
    
    <!-- Hero / Promo Carousel Banner -->
    <div class="relative overflow-hidden rounded-3xl bg-linear-to-r from-red-600 via-rose-600 to-orange-500 text-white p-8 sm:p-10 shadow-lg">
      <div class="max-w-2xl space-y-3 relative z-10">
        <span class="inline-flex items-center gap-1.5 px-3.5 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-extrabold uppercase tracking-wider text-white">
          <span>⚡</span> Exclusive Promo Codes
        </span>
        <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
          Craving something delicious today?
        </h1>
        <p class="text-sm sm:text-base text-red-100 font-medium leading-relaxed">
          Order from the finest rated restaurants in <span class="font-bold text-white underline underline-offset-4 decoration-amber-300">{{ restaurantStore.selectedCity }}</span> with lightning-fast delivery.
        </p>
      </div>

      <!-- Quick Copy Promo Chips -->
      <div class="mt-8 relative z-10 space-y-2">
        <div class="text-[11px] font-bold text-red-200 uppercase tracking-wider">
          Tap any code to copy:
        </div>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="offer in featuredOffers"
            :key="offer.code"
            type="button"
            @click="copyCode(offer.code)"
            class="px-4 py-2 bg-white/15 hover:bg-white/25 border border-white/25 backdrop-blur-md rounded-2xl text-xs font-bold text-white transition-all cursor-pointer flex items-center gap-2 active:scale-95 shadow-xs"
          >
            <span class="font-extrabold tracking-wider bg-white/20 px-2 py-0.5 rounded-lg">{{ offer.code }}</span>
            <span class="text-red-100 font-medium">{{ offer.text }}</span>
            <span v-if="copiedCoupon === offer.code" class="text-[10px] bg-white text-zomato-red font-extrabold px-2 py-0.5 rounded-md shadow-xs">
              ✓ Copied!
            </span>
          </button>
        </div>
      </div>

      <!-- Subtle background decorations -->
      <div class="absolute -right-12 -bottom-12 w-80 h-80 bg-white/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute right-1/4 -top-12 w-60 h-60 bg-amber-400/20 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- Top Picks Near You Section -->
    <section v-if="!restaurantStore.searchQuery && restaurantStore.topPicks.length > 0" class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-surface-dark tracking-tight">
            Top Picks Near You
          </h2>
          <p class="text-xs sm:text-sm text-surface-muted mt-0.5">
            Highest-rated culinary spots in {{ restaurantStore.selectedCity }}
          </p>
        </div>
      </div>

      <!-- Top Picks Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        <RestaurantCard
          v-for="restaurant in restaurantStore.topPicks.slice(0, 3)"
          :key="`top-${restaurant.id}`"
          :restaurant="restaurant"
        />
      </div>
    </section>

    <!-- Main Restaurant Discovery Grid -->
    <section class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-surface-dark tracking-tight">
            {{ restaurantStore.searchQuery ? `Search results for "${restaurantStore.searchQuery}"` : `Explore Restaurants in ${restaurantStore.selectedCity}` }}
          </h2>
          <p class="text-xs sm:text-sm text-surface-muted mt-0.5">
            {{ restaurantStore.restaurants.length }} curated spots delivering to your location
          </p>
        </div>
      </div>

      <!-- Filters -->
      <FilterSidebar />

      <!-- Loading Skeletons -->
      <div v-if="restaurantStore.loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        <div
          v-for="n in 6"
          :key="n"
          class="bg-white rounded-3xl border border-gray-200/80 overflow-hidden p-5 animate-pulse space-y-4 shadow-card"
        >
          <div class="aspect-16/9 bg-gray-200 rounded-2xl"></div>
          <div class="flex justify-between items-center">
            <div class="h-5 bg-gray-200 rounded-lg w-1/2"></div>
            <div class="h-5 bg-gray-200 rounded-lg w-12"></div>
          </div>
          <div class="h-4 bg-gray-200 rounded-lg w-3/4"></div>
          <div class="h-4 bg-gray-200 rounded-lg w-1/3 pt-2"></div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="restaurantStore.restaurants.length === 0"
        class="text-center py-20 px-6 bg-white rounded-3xl border border-gray-200 shadow-card space-y-4 max-w-lg mx-auto"
      >
        <div class="text-5xl">🍽️</div>
        <h3 class="text-xl font-extrabold text-surface-dark">
          No restaurants match your criteria
        </h3>
        <p class="text-xs sm:text-sm text-surface-muted max-w-sm mx-auto leading-relaxed">
          Try adjusting or clearing your filters to discover more places in {{ restaurantStore.selectedCity }}.
        </p>
        <button
          type="button"
          @click="restaurantStore.resetFilters"
          class="px-6 py-3 bg-zomato-red hover:bg-zomato-red-dark text-white text-xs font-extrabold uppercase tracking-wider rounded-2xl transition cursor-pointer shadow-xs active:scale-95"
        >
          Reset All Filters
        </button>
      </div>

      <!-- Discovery Grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        <RestaurantCard
          v-for="restaurant in restaurantStore.restaurants"
          :key="restaurant.id"
          :restaurant="restaurant"
        />
      </div>
    </section>

  </div>
</template>
