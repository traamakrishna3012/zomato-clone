<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const mobile = ref('')
const otp = ref('')
const fullName = ref('')
const localError = ref('')

function handleSendOtp() {
  localError.value = ''
  const cleaned = mobile.value.replace(/\D/g, '')
  if (cleaned.length < 10) {
    localError.value = 'Please enter a valid 10-digit mobile number.'
    return
  }
  authStore.sendOtp(cleaned).catch(() => {
    // Error is set in store
  })
}

function handleVerifyOtp() {
  localError.value = ''
  const cleanedOtp = otp.value.replace(/\D/g, '')
  if (cleanedOtp.length !== 6) {
    localError.value = 'Please enter a 6-digit OTP.'
    return
  }
  authStore.verifyOtp(authStore.activeMobile, cleanedOtp, fullName.value.trim()).catch(() => {
    // Error is set in store
  })
}

function handleClose() {
  mobile.value = ''
  otp.value = ''
  fullName.value = ''
  localError.value = ''
  authStore.closeAuthModal()
}
</script>

<template>
  <div
    v-if="authStore.isAuthModalOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs transition-opacity"
    @click.self="handleClose"
  >
    <div class="bg-white rounded-2xl max-w-md w-full p-6 sm:p-8 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
      <!-- Close Button -->
      <button
        type="button"
        class="absolute top-4 right-4 text-surface-muted hover:text-surface-dark p-2 rounded-full hover:bg-gray-100 transition cursor-pointer"
        @click="handleClose"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Step 1: Enter Mobile Number -->
      <div v-if="authStore.authStep === 'mobile'">
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-surface-dark mb-1">
            Login or Sign Up
          </h2>
          <p class="text-sm text-surface-muted">
            Enter your mobile number to get an instant verification code.
          </p>
        </div>

        <div v-if="localError || authStore.error" class="mb-4 p-3 bg-red-50 border border-red-200 text-zomato-red rounded-lg text-sm">
          {{ localError || authStore.error }}
        </div>

        <form @submit.prevent="handleSendOtp" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-surface-muted uppercase tracking-wider mb-2">
              Phone Number
            </label>
            <div class="flex rounded-xl border border-card-border overflow-hidden focus-within:border-zomato-red focus-within:ring-1 focus-within:ring-zomato-red transition">
              <span class="inline-flex items-center px-3 bg-gray-50 text-surface-dark font-medium border-r border-card-border text-sm">
                🇮🇳 +91
              </span>
              <input
                v-model="mobile"
                type="tel"
                maxlength="10"
                placeholder="Enter 10-digit mobile"
                class="flex-1 px-4 py-3 text-sm focus:outline-none"
                autofocus
              />
            </div>
          </div>

          <button
            type="submit"
            :disabled="authStore.isLoading || !mobile"
            class="w-full py-3 bg-zomato-red hover:bg-zomato-red-dark text-white font-semibold rounded-xl shadow-sm transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
          >
            <span v-if="authStore.isLoading" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>Send OTP</span>
          </button>
        </form>

        <p class="mt-6 text-xs text-center text-surface-muted">
          By continuing, you agree to our Terms of Service & Privacy Policy.
        </p>
      </div>

      <!-- Step 2: Verify OTP -->
      <div v-else-if="authStore.authStep === 'otp'">
        <div class="mb-6">
          <div class="flex items-center gap-2 mb-1">
            <button
              type="button"
              class="text-surface-muted hover:text-surface-dark text-sm p-1 rounded-md hover:bg-gray-100 transition"
              @click="authStore.authStep = 'mobile'"
            >
              ← Back
            </button>
            <h2 class="text-2xl font-bold text-surface-dark">
              Verify OTP
            </h2>
          </div>
          <p class="text-sm text-surface-muted">
            Code sent to <span class="font-semibold text-surface-dark">+91 {{ authStore.activeMobile }}</span>
          </p>
        </div>

        <div v-if="localError || authStore.error" class="mb-4 p-3 bg-red-50 border border-red-200 text-zomato-red rounded-lg text-sm">
          {{ localError || authStore.error }}
        </div>

        <div class="mb-4 p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg text-xs">
          💡 Development Code: <span class="font-bold">123456</span>
        </div>

        <form @submit.prevent="handleVerifyOtp" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-surface-muted uppercase tracking-wider mb-2">
              Full Name <span class="text-gray-400 font-normal">(optional)</span>
            </label>
            <input
              v-model="fullName"
              type="text"
              placeholder="e.g. Aman Sharma"
              class="w-full px-4 py-3 rounded-xl border border-card-border focus:border-zomato-red focus:ring-1 focus:ring-zomato-red text-sm outline-none transition"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-surface-muted uppercase tracking-wider mb-2">
              6-Digit Verification Code
            </label>
            <input
              v-model="otp"
              type="text"
              maxlength="6"
              placeholder="Enter 6-digit OTP"
              class="w-full px-4 py-3 rounded-xl border border-card-border focus:border-zomato-red focus:ring-1 focus:ring-zomato-red text-center tracking-widest text-lg font-bold outline-none transition"
              autofocus
            />
          </div>

          <button
            type="submit"
            :disabled="authStore.isLoading || otp.length !== 6"
            class="w-full py-3 bg-zomato-red hover:bg-zomato-red-dark text-white font-semibold rounded-xl shadow-sm transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
          >
            <span v-if="authStore.isLoading" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>Verify & Continue</span>
          </button>
        </form>

        <div class="mt-4 text-center">
          <button
            type="button"
            class="text-xs font-medium text-zomato-red hover:underline cursor-pointer"
            @click="handleSendOtp"
          >
            Resend OTP
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
