<script setup>
import { useRestaurantStore } from '../stores/restaurant'

const restaurantStore = useRestaurantStore()

const cuisines = [
  'North Indian',
  'Chinese',
  'Italian',
  'Street Food',
  'Fast Food & Desserts',
  'Mughlai & Biryani',
]

function handleCuisineClick(cuisine) {
  if (restaurantStore.filters.cuisine === cuisine) {
    restaurantStore.setFilter('cuisine', '')
  } else {
    restaurantStore.setFilter('cuisine', cuisine)
  }
}
</script>

<template>
  <div class="space-y-4 mb-8 bg-white/70 backdrop-blur-xs p-5 rounded-3xl border border-gray-200/80 shadow-2xs">
    
    <!-- Row 1: Primary Quick Filter Toggles -->
    <div class="flex items-center gap-3 overflow-x-auto pb-1 scrollbar-none">
      
      <!-- Clear Filters Button -->
      <button
        v-if="restaurantStore.hasActiveFilters"
        type="button"
        @click="restaurantStore.resetFilters"
        class="inline-flex items-center gap-1.5 px-4 py-2 bg-red-50 hover:bg-red-100 text-zomato-red border border-red-200 rounded-2xl text-xs font-bold shrink-0 transition cursor-pointer shadow-2xs"
      >
        <span>✕</span>
        <span>Clear All</span>
      </button>

      <!-- Pure Veg Toggle -->
      <button
        type="button"
        @click="restaurantStore.toggleFilter('isPureVeg')"
        :class="[
          'inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold shrink-0 transition cursor-pointer border shadow-2xs',
          restaurantStore.filters.isPureVeg
            ? 'bg-veg-green text-white border-veg-green shadow-xs scale-102'
            : 'bg-white text-surface-dark border-gray-200 hover:bg-gray-50'
        ]"
      >
        <span>🌱</span>
        <span>Pure Veg</span>
      </button>

      <!-- 4.0+ Rating Toggle -->
      <button
        type="button"
        @click="restaurantStore.setFilter('minRating', restaurantStore.filters.minRating === 4.0 ? null : 4.0)"
        :class="[
          'inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold shrink-0 transition cursor-pointer border shadow-2xs',
          restaurantStore.filters.minRating === 4.0
            ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs scale-102'
            : 'bg-white text-surface-dark border-gray-200 hover:bg-gray-50'
        ]"
      >
        <span>⭐</span>
        <span>Rating 4.0+</span>
      </button>

      <!-- Fast Delivery Toggle -->
      <button
        type="button"
        @click="restaurantStore.toggleFilter('fastDelivery')"
        :class="[
          'inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold shrink-0 transition cursor-pointer border shadow-2xs',
          restaurantStore.filters.fastDelivery
            ? 'bg-zomato-red text-white border-zomato-red shadow-xs scale-102'
            : 'bg-white text-surface-dark border-gray-200 hover:bg-gray-50'
        ]"
      >
        <span>⚡</span>
        <span>Fast Delivery (&lt;30 mins)</span>
      </button>

      <!-- Cost for Two Filter -->
      <button
        type="button"
        @click="restaurantStore.setFilter('maxCost', restaurantStore.filters.maxCost === 400 ? null : 400)"
        :class="[
          'inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold shrink-0 transition cursor-pointer border shadow-2xs',
          restaurantStore.filters.maxCost === 400
            ? 'bg-surface-dark text-white border-surface-dark shadow-xs scale-102'
            : 'bg-white text-surface-dark border-gray-200 hover:bg-gray-50'
        ]"
      >
        <span>💰</span>
        <span>Under ₹400</span>
      </button>
    </div>

    <!-- Row 2: Cuisine Chips -->
    <div class="flex items-center gap-2 overflow-x-auto pt-2 border-t border-gray-100 scrollbar-none text-xs">
      <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px] shrink-0 mr-1">
        Cuisines:
      </span>
      <button
        v-for="c in cuisines"
        :key="c"
        type="button"
        @click="handleCuisineClick(c)"
        :class="[
          'px-3.5 py-1.5 rounded-xl font-bold shrink-0 transition cursor-pointer border text-xs',
          restaurantStore.filters.cuisine === c
            ? 'bg-zomato-red text-white border-zomato-red shadow-xs'
            : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50 hover:text-surface-dark'
        ]"
      >
        {{ c }}
      </button>
    </div>
  </div>
</template>
