<script setup>
import { ref } from 'vue'
import api from '../services/api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  order: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close', 'success'])

const activeTab = ref('upi') // 'upi', 'card', 'netbanking'
const upiId = ref('user@okhdfcbank')
const isProcessing = ref(false)
const isSuccess = ref(false)
const errorMessage = ref('')

async function simulatePaymentSuccess(methodName = 'UPI') {
  if (!props.order) return

  isProcessing.value = true
  errorMessage.value = ''

  try {
    // 1. Create test Razorpay Order
    const rzpOrderResp = await api.post('/payments/create-razorpay-order/', {
      order_id: props.order.id,
    })

    const rzpOrderId = rzpOrderResp.data.razorpay_order_id
    const fakePaymentId = `pay_${methodName.toLowerCase()}_${Date.now().toString(36)}`

    // Small delay to simulate gateway authorization
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // 2. Verify payment on backend
    const verifyResp = await api.post('/payments/verify-razorpay-payment/', {
      order_id: props.order.id,
      razorpay_payment_id: fakePaymentId,
      razorpay_order_id: rzpOrderId,
    })

    isProcessing.value = false
    isSuccess.value = true

    setTimeout(() => {
      emit('success', verifyResp.data.order)
    }, 1200)
  } catch (err) {
    isProcessing.value = false
    errorMessage.value = err.response?.data?.detail || 'Payment authorization failed. Please retry.'
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200"
  >
    <div
      class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-gray-100 animate-in zoom-in-95 duration-200"
    >
      <!-- Razorpay Header -->
      <div class="bg-[#0c2340] text-white p-5 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-[#3395ff] flex items-center justify-center font-extrabold text-white text-base shadow-sm">
            R
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold tracking-wide">Razorpay</span>
              <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-400 text-gray-900 tracking-wider">
                TEST MODE
              </span>
            </div>
            <p class="text-[11px] text-gray-300">
              {{ order?.restaurant_name || 'Zomato Food Delivery' }}
            </p>
          </div>
        </div>

        <div class="text-right">
          <span class="text-xs text-gray-300 block">Amount</span>
          <span class="text-lg font-extrabold text-white">
            ₹{{ order ? parseFloat(order.grand_total).toFixed(0) : '0' }}
          </span>
        </div>
      </div>

      <!-- Processing State -->
      <div v-if="isProcessing" class="p-10 text-center space-y-4">
        <div class="w-12 h-12 border-3 border-[#3395ff] border-t-transparent rounded-full animate-spin mx-auto"></div>
        <h4 class="text-base font-bold text-gray-800">
          Authorizing payment...
        </h4>
        <p class="text-xs text-gray-500">
          Connecting to Razorpay Test Gateway. Please do not close or refresh.
        </p>
      </div>

      <!-- Success State -->
      <div v-else-if="isSuccess" class="p-10 text-center space-y-4">
        <div class="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto text-2xl font-bold">
          ✓
        </div>
        <h4 class="text-lg font-bold text-gray-900">
          Payment Successful!
        </h4>
        <p class="text-xs text-gray-500">
          Your payment of ₹{{ order ? parseFloat(order.grand_total).toFixed(0) : '0' }} is verified. Redirecting...
        </p>
      </div>

      <!-- Payment Method Selection -->
      <div v-else class="p-6 space-y-5">
        <!-- Error Banner -->
        <div v-if="errorMessage" class="p-3 bg-red-50 text-red-600 text-xs rounded-xl border border-red-200">
          {{ errorMessage }}
        </div>

        <!-- Tabs -->
        <div class="flex items-center bg-gray-100 rounded-2xl p-1 text-xs font-bold text-gray-600">
          <button
            type="button"
            @click="activeTab = 'upi'"
            :class="[
              'flex-1 py-2 rounded-xl transition cursor-pointer',
              activeTab === 'upi' ? 'bg-white text-[#0c2340] shadow-xs' : 'hover:text-gray-900'
            ]"
          >
            📱 UPI
          </button>
          <button
            type="button"
            @click="activeTab = 'card'"
            :class="[
              'flex-1 py-2 rounded-xl transition cursor-pointer',
              activeTab === 'card' ? 'bg-white text-[#0c2340] shadow-xs' : 'hover:text-gray-900'
            ]"
          >
            💳 Card
          </button>
          <button
            type="button"
            @click="activeTab = 'netbanking'"
            :class="[
              'flex-1 py-2 rounded-xl transition cursor-pointer',
              activeTab === 'netbanking' ? 'bg-white text-[#0c2340] shadow-xs' : 'hover:text-gray-900'
            ]"
          >
            🏦 Netbanking
          </button>
        </div>

        <!-- UPI Tab Content -->
        <div v-if="activeTab === 'upi'" class="space-y-4">
          <div class="p-4 bg-gray-50 border border-gray-200 rounded-2xl flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="text-3xl">📲</div>
              <div>
                <div class="text-xs font-bold text-gray-800">Scan UPI QR Code</div>
                <div class="text-[11px] text-gray-500">Google Pay, PhonePe, Paytm, BHIM</div>
              </div>
            </div>
            <button
              type="button"
              @click="simulatePaymentSuccess('UPI')"
              class="px-3.5 py-1.5 bg-[#3395ff] hover:bg-[#2082eb] text-white text-xs font-bold rounded-xl transition cursor-pointer"
            >
              Simulate Scan & Pay
            </button>
          </div>

          <div class="relative flex items-center justify-center">
            <span class="bg-white px-3 text-[11px] font-semibold text-gray-400">OR ENTER VPA</span>
            <div class="absolute inset-x-0 border-t border-gray-100 -z-10"></div>
          </div>

          <div class="space-y-2">
            <input
              v-model="upiId"
              type="text"
              placeholder="e.g. mobile@upi or name@okaxis"
              class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs focus:bg-white focus:border-[#3395ff] focus:outline-none transition"
            />
            <button
              type="button"
              @click="simulatePaymentSuccess('UPI')"
              class="w-full py-3 bg-[#3395ff] hover:bg-[#2082eb] text-white text-xs font-extrabold rounded-xl transition cursor-pointer shadow-xs"
            >
              Pay ₹{{ order ? parseFloat(order.grand_total).toFixed(0) : '0' }} via UPI
            </button>
          </div>
        </div>

        <!-- Card Tab Content -->
        <div v-else-if="activeTab === 'card'" class="space-y-3">
          <div>
            <label class="text-[11px] font-semibold text-gray-500 block mb-1">Card Number</label>
            <input
              type="text"
              value="4111 •••• •••• 1111"
              readonly
              class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-mono text-gray-700"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-[11px] font-semibold text-gray-500 block mb-1">Valid Thru</label>
              <input
                type="text"
                value="12 / 28"
                readonly
                class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-mono text-gray-700"
              />
            </div>
            <div>
              <label class="text-[11px] font-semibold text-gray-500 block mb-1">CVV</label>
              <input
                type="password"
                value="•••"
                readonly
                class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-mono text-gray-700"
              />
            </div>
          </div>

          <button
            type="button"
            @click="simulatePaymentSuccess('Card')"
            class="w-full py-3 bg-[#3395ff] hover:bg-[#2082eb] text-white text-xs font-extrabold rounded-xl transition cursor-pointer shadow-xs mt-2"
          >
            Pay ₹{{ order ? parseFloat(order.grand_total).toFixed(0) : '0' }} with Test Card
          </button>
        </div>

        <!-- Netbanking Tab Content -->
        <div v-else-if="activeTab === 'netbanking'" class="space-y-3">
          <div class="grid grid-cols-2 gap-2 text-xs">
            <button
              v-for="bank in ['HDFC Bank', 'ICICI Bank', 'State Bank of India', 'Axis Bank', 'Kotak Bank', 'Other Banks']"
              :key="bank"
              type="button"
              @click="simulatePaymentSuccess('Netbanking')"
              class="p-3 border border-gray-200 hover:border-[#3395ff] hover:bg-blue-50/50 rounded-xl text-left font-semibold text-gray-700 transition cursor-pointer"
            >
              {{ bank }}
            </button>
          </div>
        </div>

        <!-- Footer Notice -->
        <div class="pt-3 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-400">
          <span>🔒 256-bit SSL encrypted</span>
          <button
            type="button"
            @click="emit('close')"
            class="text-gray-500 hover:text-gray-800 font-semibold cursor-pointer"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
