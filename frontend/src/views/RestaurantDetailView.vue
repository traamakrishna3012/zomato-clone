<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRestaurantStore } from '../stores/restaurant'
import { useAuthStore } from '../stores/auth'
import MenuItemCard from '../components/MenuItemCard.vue'

const route = useRoute()
const restaurantStore = useRestaurantStore()
const authStore = useAuthStore()

const activeCategory = ref('All')
const vegOnlyFilter = ref(false)

// Review form state
const newRating = ref(5)
const newComment = ref('')
const isSubmittingReview = ref(false)
const reviewMessage = ref('')

const categories = ['All', 'Starters', 'Main Course', 'Desserts', 'Beverages']

onMounted(() => {
  const restaurantId = route.params.id
  restaurantStore.fetchRestaurantDetail(restaurantId)
})

const restaurant = computed(() => restaurantStore.activeRestaurant)

const filteredMenuItems = computed(() => {
  if (!restaurant.value?.menu_items) return []
  return restaurant.value.menu_items.filter((item) => {
    const matchesCategory = activeCategory.value === 'All' || item.category === activeCategory.value
    const matchesVeg = !vegOnlyFilter.value || item.is_veg
    return matchesCategory && matchesVeg
  })
})

const groupedMenu = computed(() => {
  const groups = {}
  filteredMenuItems.value.forEach((item) => {
    if (!groups[item.category]) {
      groups[item.category] = []
    }
    groups[item.category].push(item)
  })
  return groups
})

const ratingBadgeClass = computed(() => {
  if (!restaurant.value) return 'bg-rating-green text-white'
  const r = parseFloat(restaurant.value.rating)
  if (r >= 4.0) return 'bg-rating-green text-white'
  if (r >= 3.0) return 'bg-rating-yellow text-white'
  return 'bg-rating-red text-white'
})

async function handleReviewSubmit() {
  if (!newComment.value.trim() || !restaurant.value) return
  isSubmittingReview.value = true
  reviewMessage.value = ''
  try {
    await restaurantStore.addReview(restaurant.value.id, newRating.value, newComment.value.trim())
    newComment.value = ''
    newRating.value = 5
    reviewMessage.value = 'Thank you for your review!'
  } catch (err) {
    reviewMessage.value = 'Failed to submit review.'
  } finally {
    isSubmittingReview.value = false
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto pb-16">
    <!-- Loading State -->
    <div v-if="restaurantStore.detailLoading" class="animate-pulse space-y-6">
      <div class="h-64 bg-gray-200 rounded-3xl"></div>
      <div class="h-8 bg-gray-200 rounded w-1/3"></div>
      <div class="h-4 bg-gray-200 rounded w-1/4"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="restaurantStore.error || !restaurant" class="text-center py-16 bg-white rounded-3xl border border-card-border p-6">
      <div class="text-4xl mb-3">😕</div>
      <h3 class="text-lg font-bold text-surface-dark mb-2">Restaurant Not Found</h3>
      <RouterLink to="/" class="px-5 py-2.5 bg-zomato-red text-white font-semibold rounded-xl text-xs inline-block">
        Back to Home
      </RouterLink>
    </div>

    <!-- Restaurant Content -->
    <div v-else class="space-y-8">
      
      <!-- Restaurant Header Card -->
      <div class="bg-white rounded-3xl border border-card-border overflow-hidden shadow-xs">
        <!-- Cover Image Banner -->
        <div class="relative h-60 sm:h-72 w-full bg-gray-100">
          <img
            :src="restaurant.image_url || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1000&auto=format&fit=crop&q=80'"
            :alt="restaurant.name"
            class="w-full h-full object-cover"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent"></div>
          
          <div class="absolute bottom-6 left-6 right-6 text-white flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-1.5">
                <span
                  v-if="restaurant.is_pure_veg"
                  class="bg-veg-green text-white text-[11px] font-bold px-2 py-0.5 rounded-full"
                >
                  🌱 PURE VEG
                </span>
                <span class="text-xs font-semibold text-gray-200 uppercase tracking-wider">
                  {{ restaurant.cuisine }}
                </span>
              </div>
              <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight">
                {{ restaurant.name }}
              </h1>
              <p class="text-xs sm:text-sm text-gray-200 mt-1">
                📍 {{ restaurant.address }}, {{ restaurant.city }}
              </p>
            </div>

            <!-- Rating & Delivery Box -->
            <div class="flex items-center gap-3 shrink-0">
              <div class="bg-black/60 backdrop-blur-md px-3.5 py-2 rounded-2xl border border-white/10 text-center">
                <div class="text-xs text-gray-300">Delivery Time</div>
                <div class="text-sm font-bold">⏱ {{ restaurant.delivery_time }} mins</div>
              </div>

              <div class="bg-black/60 backdrop-blur-md px-3.5 py-2 rounded-2xl border border-white/10 text-center">
                <div class="text-xs text-gray-300">Cost for two</div>
                <div class="text-sm font-bold">₹{{ restaurant.avg_cost_for_two }}</div>
              </div>

              <div
                :class="[ratingBadgeClass, 'px-3.5 py-2 rounded-2xl text-center shadow-md font-bold']"
              >
                <div class="text-xs text-white/90">Rating</div>
                <div class="text-sm flex items-center justify-center gap-0.5">
                  <span>{{ parseFloat(restaurant.rating).toFixed(1) }}</span>
                  <span class="text-xs">★</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Menu Section -->
      <section class="bg-white rounded-3xl border border-card-border p-6 sm:p-8 shadow-xs">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-card-border">
          <div>
            <h2 class="text-xl font-bold text-surface-dark">
              Menu
            </h2>
            <p class="text-xs text-surface-muted">
              {{ restaurant.menu_items?.length || 0 }} items available
            </p>
          </div>

          <!-- Veg Only Toggle -->
          <button
            type="button"
            @click="vegOnlyFilter = !vegOnlyFilter"
            :class="[
              'inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold border transition cursor-pointer self-start sm:self-auto',
              vegOnlyFilter ? 'bg-veg-green text-white border-veg-green' : 'bg-gray-50 text-surface-dark border-card-border hover:bg-gray-100'
            ]"
          >
            <span>🌱</span>
            <span>Veg Only</span>
          </button>
        </div>

        <!-- Category Tabs -->
        <div class="flex items-center gap-2 overflow-x-auto py-4 scrollbar-none border-b border-card-border text-xs sm:text-sm">
          <button
            v-for="cat in categories"
            :key="cat"
            type="button"
            @click="activeCategory = cat"
            :class="[
              'px-4 py-2 rounded-xl font-semibold shrink-0 transition cursor-pointer',
              activeCategory === cat
                ? 'bg-zomato-red text-white shadow-xs'
                : 'text-surface-muted hover:text-surface-dark hover:bg-gray-100'
            ]"
          >
            {{ cat }}
          </button>
        </div>

        <!-- Menu Item Cards List -->
        <div class="pt-4 divide-y divide-card-border">
          <div
            v-for="(items, categoryName) in groupedMenu"
            :key="categoryName"
            class="py-4 first:pt-0"
          >
            <h3 class="text-base font-extrabold text-surface-dark uppercase tracking-wider mb-2 text-zomato-red">
              {{ categoryName }} ({{ items.length }})
            </h3>
            <div>
              <MenuItemCard
                v-for="item in items"
                :key="item.id"
                :item="item"
                :restaurant="restaurant"
              />
            </div>
          </div>

          <div v-if="filteredMenuItems.length === 0" class="text-center py-12 text-surface-muted text-sm">
            No dishes found for this category filter.
          </div>
        </div>
      </section>

      <!-- Customer Reviews Section -->
      <section class="bg-white rounded-3xl border border-card-border p-6 sm:p-8 shadow-xs">
        <div class="flex items-center justify-between mb-6 pb-4 border-b border-card-border">
          <div>
            <h2 class="text-xl font-bold text-surface-dark">
              Customer Reviews & Ratings
            </h2>
            <p class="text-xs text-surface-muted">
              {{ restaurant.reviews?.length || 0 }} reviews from happy foodies
            </p>
          </div>
        </div>

        <!-- Add Review Form -->
        <div class="mb-8 p-5 bg-gray-50 rounded-2xl border border-card-border">
          <h3 class="text-sm font-bold text-surface-dark mb-3">
            Write a Review
          </h3>

          <div v-if="!authStore.isAuthenticated" class="text-xs text-surface-muted">
            <span>Please </span>
            <button
              type="button"
              @click="authStore.openAuthModal('mobile')"
              class="text-zomato-red font-bold hover:underline cursor-pointer"
            >
              log in
            </button>
            <span> to rate and review this restaurant.</span>
          </div>

          <form v-else @submit.prevent="handleReviewSubmit" class="space-y-3">
            <div class="flex items-center gap-3">
              <label class="text-xs font-semibold text-surface-muted">Rating:</label>
              <div class="flex items-center gap-1">
                <button
                  v-for="star in 5"
                  :key="star"
                  type="button"
                  @click="newRating = star"
                  class="text-lg transition cursor-pointer"
                  :class="star <= newRating ? 'text-amber-500' : 'text-gray-300'"
                >
                  ★
                </button>
              </div>
              <span class="text-xs font-bold text-surface-dark">{{ newRating }}/5</span>
            </div>

            <textarea
              v-model="newComment"
              rows="2"
              placeholder="Share your experience (e.g. Delicious food, fast delivery...)"
              class="w-full px-4 py-2.5 rounded-xl border border-card-border bg-white text-xs sm:text-sm focus:border-zomato-red focus:outline-none transition"
              required
            ></textarea>

            <div class="flex items-center justify-between">
              <span v-if="reviewMessage" class="text-xs text-veg-green font-semibold">
                {{ reviewMessage }}
              </span>
              <button
                type="submit"
                :disabled="isSubmittingReview || !newComment.trim()"
                class="px-5 py-2 bg-zomato-red hover:bg-zomato-red-dark text-white font-bold rounded-xl text-xs transition disabled:opacity-50 cursor-pointer ml-auto"
              >
                Submit Review
              </button>
            </div>
          </form>
        </div>

        <!-- Review List -->
        <div v-if="restaurant.reviews?.length > 0" class="space-y-4">
          <div
            v-for="review in restaurant.reviews"
            :key="review.id"
            class="p-4 rounded-2xl bg-white border border-card-border space-y-1.5"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-zomato-red/10 text-zomato-red font-bold text-xs flex items-center justify-center">
                  {{ review.user_name?.[0]?.toUpperCase() || 'U' }}
                </div>
                <span class="text-xs font-bold text-surface-dark">
                  {{ review.user_name }}
                </span>
              </div>

              <span class="inline-flex items-center gap-0.5 px-2 py-0.5 bg-rating-green text-white text-[11px] font-bold rounded-md">
                <span>{{ review.rating }}</span>
                <span class="text-[9px]">★</span>
              </span>
            </div>

            <p v-if="review.comment" class="text-xs text-surface-dark pl-9">
              {{ review.comment }}
            </p>
          </div>
        </div>

        <div v-else class="text-center py-6 text-xs text-surface-muted">
          No reviews yet. Be the first to review!
        </div>
      </section>

    </div>
  </div>
</template>
