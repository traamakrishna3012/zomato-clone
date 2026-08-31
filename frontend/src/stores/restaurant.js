import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useRestaurantStore = defineStore('restaurant', () => {
  const restaurants = ref([])
  const topPicks = ref([])
  const activeRestaurant = ref(null)
  const loading = ref(false)
  const detailLoading = ref(false)
  const error = ref(null)
  const selectedCity = ref('Indore')
  const searchQuery = ref('')
  
  const filters = ref({
    cuisine: '',
    minRating: null,
    maxCost: null,
    isPureVeg: false,
    fastDelivery: false,
  })

  const hasActiveFilters = computed(() => {
    return !!(
      filters.value.cuisine ||
      filters.value.minRating ||
      filters.value.maxCost ||
      filters.value.isPureVeg ||
      filters.value.fastDelivery ||
      searchQuery.value
    )
  })

  async function fetchRestaurants() {
    loading.value = true
    error.value = null

    try {
      const params = {}
      if (selectedCity.value) params.city = selectedCity.value
      if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
      if (filters.value.cuisine) params.cuisine = filters.value.cuisine
      if (filters.value.minRating) params.min_rating = filters.value.minRating
      if (filters.value.maxCost) params.max_cost = filters.value.maxCost
      if (filters.value.isPureVeg) params.is_pure_veg = 'true'
      if (filters.value.fastDelivery) params.fast_delivery = 'true'

      const response = await api.get('/restaurants/', { params })
      restaurants.value = response.data.results || response.data
      return response.data
    } catch (err) {
      error.value = 'Failed to load restaurants.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTopPicks() {
    try {
      const response = await api.get('/restaurants/top-picks/')
      topPicks.value = response.data.results || response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch top picks', err)
    }
  }

  async function fetchRestaurantDetail(id) {
    detailLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/restaurants/${id}/`)
      activeRestaurant.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Failed to load restaurant details.'
      throw err
    } finally {
      detailLoading.value = false
    }
  }

  async function addReview(restaurantId, rating, comment) {
    const response = await api.post('/reviews/', {
      restaurant: restaurantId,
      rating,
      comment,
    })
    // Refresh active restaurant detail to show new review and updated rating
    if (activeRestaurant.value && activeRestaurant.value.id === restaurantId) {
      await fetchRestaurantDetail(restaurantId)
    }
    return response.data
  }

  function setFilter(key, value) {
    filters.value[key] = value
    fetchRestaurants()
  }

  function toggleFilter(key) {
    filters.value[key] = !filters.value[key]
    fetchRestaurants()
  }

  function resetFilters() {
    filters.value = {
      cuisine: '',
      minRating: null,
      maxCost: null,
      isPureVeg: false,
      fastDelivery: false,
    }
    searchQuery.value = ''
    fetchRestaurants()
  }

  function setCity(city) {
    selectedCity.value = city
    fetchRestaurants()
    fetchTopPicks()
  }

  return {
    restaurants,
    topPicks,
    activeRestaurant,
    loading,
    detailLoading,
    error,
    selectedCity,
    searchQuery,
    filters,
    hasActiveFilters,
    fetchRestaurants,
    fetchTopPicks,
    fetchRestaurantDetail,
    addReview,
    setFilter,
    toggleFilter,
    resetFilters,
    setCity,
  }
})
