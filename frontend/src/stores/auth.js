import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)
  const isLoading = ref(false)
  const error = ref(null)
  const isAuthModalOpen = ref(false)
  const authStep = ref('mobile') // 'mobile' | 'otp'
  const activeMobile = ref('')

  const isAuthenticated = computed(() => !!token.value)

  function loadUserFromStorage() {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')
    if (storedToken) {
      token.value = storedToken
    }
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        user.value = null
      }
    }
  }

  function openAuthModal(step = 'mobile') {
    authStep.value = step
    error.value = null
    isAuthModalOpen.value = true
  }

  function closeAuthModal() {
    isAuthModalOpen.value = false
    authStep.value = 'mobile'
    error.value = null
  }

  async function sendOtp(mobile) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/send-otp/', { mobile })
      activeMobile.value = mobile
      authStep.value = 'otp'
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.response?.data?.mobile?.[0] || 'Failed to send OTP.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function verifyOtp(mobile, otp, name = '') {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/verify-otp/', { mobile, otp, name })
      const { access, refresh, user: userData } = response.data

      token.value = access
      user.value = userData
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      closeAuthModal()
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.response?.data?.otp?.[0] || 'Invalid OTP. Please try again.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthModalOpen,
    authStep,
    activeMobile,
    isAuthenticated,
    loadUserFromStorage,
    openAuthModal,
    closeAuthModal,
    sendOtp,
    verifyOtp,
    logout,
  }
})
