<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import OrderStatusTracker from '../components/OrderStatusTracker.vue'
import api from '../services/api'

const authStore = useAuthStore()
const orders = ref([])
const loading = ref(true)
const cancellingId = ref(null)
const actionError = ref('')

async function fetchOrders() {
  if (!authStore.isAuthenticated) {
    loading.value = false
    return
  }

  loading.value = true
  try {
    const response = await api.get('/orders/')
    orders.value = response.data.results || response.data
  } catch (err) {
    console.error('Failed to load orders', err)
  } finally {
    loading.value = false
  }
}

async function handleCancelOrder(orderId) {
  cancellingId.value = orderId
  actionError.value = ''
  try {
    const response = await api.post(`/orders/${orderId}/cancel/`)
    // Update local order state
    const index = orders.value.findIndex((o) => o.id === orderId)
    if (index !== -1) {
      orders.value[index] = response.data.order
    }
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Failed to cancel order.'
  } finally {
    cancellingId.value = null
  }
}

function handleOrderUpdated(updatedOrder) {
  const index = orders.value.findIndex((o) => o.id === updatedOrder.id)
  if (index !== -1) {
    orders.value[index] = updatedOrder
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div class="max-w-4xl mx-auto py-6 space-y-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-surface-dark tracking-tight">
          My Orders
        </h1>
        <p class="text-xs sm:text-sm text-surface-muted">
          Track active orders, verify payments, and view delivery history
        </p>
      </div>
      <button
        v-if="authStore.isAuthenticated"
        type="button"
        @click="fetchOrders"
        class="text-xs font-bold text-zomato-red hover:underline cursor-pointer flex items-center gap-1"
      >
        <span>↻</span> Refresh
      </button>
    </div>

    <!-- Error Alert -->
    <div
      v-if="actionError"
      class="p-4 bg-red-50 border border-red-200 text-zomato-red rounded-2xl text-xs font-medium"
    >
      {{ actionError }}
    </div>

    <!-- Unauthenticated State -->
    <div
      v-if="!authStore.isAuthenticated"
      class="text-center py-16 bg-white rounded-3xl border border-card-border p-8 space-y-4 shadow-xs"
    >
      <div class="text-5xl">🔒</div>
      <h2 class="text-xl font-bold text-surface-dark">
        Please log in to view your orders
      </h2>
      <p class="text-sm text-surface-muted max-w-sm mx-auto">
        Sign in with your mobile number to check order history and real-time delivery status.
      </p>
      <button
        type="button"
        @click="authStore.openAuthModal('mobile')"
        class="px-6 py-3 bg-zomato-red hover:bg-zomato-red-dark text-white font-bold rounded-2xl text-xs uppercase tracking-wider transition cursor-pointer"
      >
        Log In
      </button>
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="space-y-6 animate-pulse">
      <div v-for="n in 3" :key="n" class="bg-white rounded-3xl border border-card-border p-6 space-y-4">
        <div class="h-6 bg-gray-200 rounded w-1/3"></div>
        <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        <div class="h-20 bg-gray-200 rounded"></div>
      </div>
    </div>

    <!-- Empty Orders State -->
    <div
      v-else-if="orders.length === 0"
      class="text-center py-16 bg-white rounded-3xl border border-card-border p-8 space-y-4 shadow-xs"
    >
      <div class="text-5xl">📦</div>
      <h2 class="text-xl font-bold text-surface-dark">
        No orders placed yet
      </h2>
      <p class="text-sm text-surface-muted max-w-sm mx-auto">
        Hungry? Order delicious food from your favorite local restaurants.
      </p>
      <RouterLink
        to="/"
        class="inline-block px-6 py-3 bg-zomato-red hover:bg-zomato-red-dark text-white font-bold rounded-2xl text-xs uppercase tracking-wider transition"
      >
        Order Now
      </RouterLink>
    </div>

    <!-- Orders List -->
    <div v-else class="space-y-8">
      <div
        v-for="order in orders"
        :key="order.id"
        class="bg-white rounded-3xl border border-card-border overflow-hidden shadow-xs space-y-5 p-6 sm:p-8"
      >
        <!-- Top Metadata Header -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-card-border">
          <div class="flex items-center gap-3.5">
            <div class="w-14 h-14 rounded-2xl bg-gray-100 overflow-hidden shrink-0 border border-card-border">
              <img
                :src="order.restaurant_image || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=200&auto=format&fit=crop&q=80'"
                :alt="order.restaurant_name"
                class="w-full h-full object-cover"
              />
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-lg font-bold text-surface-dark">
                  {{ order.restaurant_name }}
                </h3>
                <span class="text-xs text-surface-muted">#{{ order.id }}</span>
              </div>
              <p class="text-xs text-surface-muted">
                Placed on {{ formatDate(order.created_at) }}
              </p>
            </div>
          </div>

          <div class="flex items-center sm:flex-col sm:items-end justify-between gap-1.5">
            <div class="text-lg font-extrabold text-surface-dark">
              ₹{{ parseFloat(order.grand_total).toFixed(0) }}
            </div>
            
            <div class="flex items-center gap-2">
              <!-- Payment Mode Pill -->
              <span class="text-[11px] font-semibold text-surface-muted uppercase">
                {{ order.payment_mode }}
              </span>

              <!-- Payment Status Badge -->
              <span
                :class="[
                  'px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wide',
                  order.payment_status === 'PAID'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                ]"
              >
                {{ order.payment_status }}
              </span>
            </div>
          </div>
        </div>

        <!-- Coupon savings banner (if used) -->
        <div
          v-if="parseFloat(order.discount_amount) > 0"
          class="flex items-center justify-between px-4 py-2 bg-emerald-50 border border-emerald-100 rounded-xl text-xs text-emerald-800"
        >
          <span class="flex items-center gap-1.5 font-medium">
            <span>🏷️</span> Promo applied: <strong>{{ order.coupon_code }}</strong>
          </span>
          <span class="font-bold">
            Saved ₹{{ parseFloat(order.discount_amount).toFixed(2) }}
          </span>
        </div>

        <!-- 4-Stage Status Tracker -->
        <OrderStatusTracker :order="order" @order-updated="handleOrderUpdated" />

        <!-- Order Items List & Delivery Details -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2 text-xs">
          <!-- Items Receipt -->
          <div class="p-4 bg-gray-50 rounded-2xl border border-card-border space-y-2">
            <h4 class="font-bold text-surface-dark uppercase tracking-wider text-[11px]">
              Items Ordered
            </h4>
            <div class="divide-y divide-card-border">
              <div
                v-for="item in order.items"
                :key="item.id"
                class="flex items-center justify-between py-1.5 first:pt-0"
              >
                <span class="text-surface-dark font-medium">
                  {{ item.item_title }} <span class="text-surface-muted">× {{ item.quantity }}</span>
                </span>
                <span class="font-bold text-surface-dark">
                  ₹{{ (parseFloat(item.price) * item.quantity).toFixed(0) }}
                </span>
              </div>
            </div>

            <!-- Transaction Reference (if available) -->
            <div v-if="order.transaction_id" class="pt-2 border-t border-card-border text-[11px] text-surface-muted truncate">
              Ref: <span class="font-mono">{{ order.transaction_id }}</span>
            </div>
          </div>

          <!-- Delivery Address & Actions -->
          <div class="p-4 bg-gray-50 rounded-2xl border border-card-border flex flex-col justify-between space-y-4">
            <div>
              <h4 class="font-bold text-surface-dark uppercase tracking-wider text-[11px] mb-1">
                Delivery Address
              </h4>
              <p class="text-surface-muted leading-relaxed">
                {{ order.delivery_address }}
              </p>
            </div>

            <!-- Cancel Order Button (Only enabled when PLACED) -->
            <div v-if="order.order_status === 'PLACED'" class="pt-2">
              <button
                type="button"
                :disabled="cancellingId === order.id"
                @click="handleCancelOrder(order.id)"
                class="w-full py-2 bg-white hover:bg-red-50 text-zomato-red font-bold rounded-xl border border-red-200 text-xs transition cursor-pointer disabled:opacity-50"
              >
                <span v-if="cancellingId === order.id">Cancelling...</span>
                <span v-else>Cancel Order</span>
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
