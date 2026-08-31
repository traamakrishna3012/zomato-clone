<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useRestaurantStore } from '../stores/restaurant'
import { useCartStore } from '../stores/cart'

const router = useRouter()
const authStore = useAuthStore()
const restaurantStore = useRestaurantStore()
const cartStore = useCartStore()

const localSearch = ref(restaurantStore.searchQuery)
const isProfileMenuOpen = ref(false)
let debounceTimeout = null

// 300ms debounce to prevent API spamming
watch(localSearch, (newVal) => {
  clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    restaurantStore.searchQuery = newVal
    if (router.currentRoute.value.name !== 'home') {
      router.push({ name: 'home' })
    }
    restaurantStore.fetchRestaurants()
  }, 300)
})

function handleCityChange(event) {
  restaurantStore.setCity(event.target.value)
}

function handleLogout() {
  authStore.logout()
  isProfileMenuOpen.value = false
}
</script>

<template>
  <header class="bg-white/95 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40 transition-shadow duration-200 shadow-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20 gap-4 sm:gap-8">
        
        <!-- Left: Logo & Location -->
        <div class="flex items-center gap-4 sm:gap-6 shrink-0">
          <RouterLink
            to="/"
            class="text-3xl sm:text-4xl font-extrabold tracking-tighter text-zomato-red hover:opacity-95 transition select-none flex items-center gap-1"
          >
            zomato
          </RouterLink>

          <!-- Location Selector Pill -->
          <div class="hidden md:flex items-center gap-2 px-3.5 py-2 bg-gray-50 hover:bg-gray-100/80 border border-gray-200 rounded-2xl text-xs font-semibold text-surface-dark transition shadow-2xs">
            <span class="text-sm text-zomato-red">📍</span>
            <select
              :value="restaurantStore.selectedCity"
              @change="handleCityChange"
              class="bg-transparent focus:outline-none cursor-pointer text-xs font-bold text-surface-dark pr-1"
            >
              <option value="Indore">Indore</option>
              <option value="Bilaspur">Bilaspur</option>
              <option value="Mumbai">Mumbai</option>
              <option value="Delhi">Delhi</option>
            </select>
          </div>
        </div>

        <!-- Center: 300ms Debounced Search Bar -->
        <div class="flex-1 max-w-xl">
          <div class="relative flex items-center">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="localSearch"
              type="text"
              placeholder="Search for restaurant, cuisine, or a dish..."
              class="w-full pl-11 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-2xl text-xs sm:text-sm text-surface-dark placeholder-gray-400 focus:bg-white focus:border-zomato-red focus:ring-2 focus:ring-red-100 focus:outline-none transition shadow-2xs"
            />
            <button
              v-if="localSearch"
              @click="localSearch = ''"
              class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-700 cursor-pointer text-xs"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Right: Actions (Auth & Cart) -->
        <div class="flex items-center gap-3 sm:gap-4 shrink-0">
          <!-- Cart Button -->
          <button
            type="button"
            @click="cartStore.openDrawer"
            class="relative inline-flex items-center gap-2 px-4 py-2.5 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-2xl text-xs sm:text-sm font-bold text-surface-dark transition cursor-pointer shadow-2xs active:scale-95"
          >
            <span class="text-base">🛒</span>
            <span class="hidden sm:inline">Cart</span>
            <span
              v-if="cartStore.itemCount > 0"
              class="inline-flex items-center justify-center px-2 py-0.5 text-[11px] font-extrabold bg-zomato-red text-white rounded-full"
            >
              {{ cartStore.itemCount }}
            </span>
          </button>

          <!-- Orders Link -->
          <RouterLink
            v-if="authStore.isAuthenticated"
            to="/orders"
            class="hidden sm:inline-flex text-xs sm:text-sm font-bold text-gray-600 hover:text-zomato-red transition px-2 py-1"
          >
            Orders
          </RouterLink>

          <!-- Unauthenticated Login Button -->
          <button
            v-if="!authStore.isAuthenticated"
            type="button"
            @click="authStore.openAuthModal('mobile')"
            class="px-5 py-2.5 bg-zomato-red hover:bg-zomato-red-dark text-white text-xs sm:text-sm font-bold rounded-2xl shadow-xs hover:shadow-sm transition cursor-pointer active:scale-95"
          >
            Log in
          </button>

          <!-- Authenticated Profile Menu -->
          <div v-else class="relative">
            <button
              type="button"
              @click="isProfileMenuOpen = !isProfileMenuOpen"
              class="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-gray-50 hover:bg-gray-100 border border-gray-200 text-xs sm:text-sm font-bold text-surface-dark transition cursor-pointer shadow-2xs"
            >
              <div class="w-7 h-7 rounded-full bg-zomato-red/10 text-zomato-red font-extrabold flex items-center justify-center text-xs">
                {{ authStore.user?.full_name ? authStore.user.full_name[0].toUpperCase() : 'U' }}
              </div>
              <span class="hidden md:inline max-w-[120px] truncate">
                {{ authStore.user?.full_name || authStore.user?.mobile }}
              </span>
              <span class="text-[10px] text-gray-400">▼</span>
            </button>

            <!-- Dropdown Menu -->
            <div
              v-if="isProfileMenuOpen"
              class="absolute right-0 mt-2 w-52 bg-white rounded-2xl shadow-xl border border-gray-100 py-2 z-50 animate-in fade-in zoom-in-95 duration-150"
              @click="isProfileMenuOpen = false"
            >
              <div class="px-4 py-2.5 border-b border-gray-100 text-xs text-gray-500">
                Signed in as <br />
                <span class="font-bold text-surface-dark text-sm">{{ authStore.user?.full_name || authStore.user?.mobile }}</span>
              </div>
              <RouterLink
                to="/orders"
                class="flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm text-surface-dark hover:bg-gray-50 transition font-medium"
              >
                <span>📦</span> My Orders
              </RouterLink>
              <button
                type="button"
                @click="handleLogout"
                class="w-full text-left flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm text-zomato-red hover:bg-red-50 transition cursor-pointer font-bold"
              >
                <span>🚪</span> Log out
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  </header>
</template>
