<script setup>
import { computed } from 'vue'
import api from '../services/api'

const props = defineProps({
  order: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['order-updated'])

const steps = [
  { key: 'PLACED', label: 'Order Placed', icon: '📝' },
  { key: 'PREPARING', label: 'Preparing', icon: '🍳' },
  { key: 'OUT_FOR_DELIVERY', label: 'On The Way', icon: '🛵' },
  { key: 'DELIVERED', label: 'Delivered', icon: '✅' },
]

const currentStepIndex = computed(() => {
  if (props.order.order_status === 'CANCELLED') return -1
  return steps.findIndex((s) => s.key === props.order.order_status)
})

async function handleAdvanceStatus() {
  try {
    const response = await api.post(`/orders/${props.order.id}/progress-status/`)
    emit('order-updated', response.data)
  } catch (err) {
    console.error('Failed to advance order status', err)
  }
}
</script>

<template>
  <div class="p-4 sm:p-5 bg-white rounded-2xl border border-card-border shadow-xs">
    <!-- Cancelled State Alert -->
    <div
      v-if="order.order_status === 'CANCELLED'"
      class="p-4 bg-red-50 border border-red-200 rounded-xl text-zomato-red flex items-center gap-3 text-sm font-semibold"
    >
      <span class="text-xl">🚫</span>
      <div>
        <div class="font-bold">Order Cancelled</div>
        <div class="text-xs font-normal text-red-600">This order has been cancelled and will not be delivered.</div>
      </div>
    </div>

    <!-- 4-Stage Active Progress Line -->
    <div v-else class="space-y-6">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-bold text-surface-muted uppercase tracking-wider">
          Live Order Status
        </h4>

        <!-- Demo Stage Advance Button -->
        <button
          v-if="order.order_status !== 'DELIVERED'"
          type="button"
          @click="handleAdvanceStatus"
          class="text-[11px] font-bold text-zomato-red hover:text-zomato-red-dark hover:underline flex items-center gap-1 cursor-pointer"
          title="Simulate order progressing to next stage"
        >
          <span>Advance Stage</span>
          <span>⚡</span>
        </button>
      </div>

      <!-- Step Nodes & Connecting Line -->
      <div class="relative flex items-center justify-between">
        <!-- Background Track Line -->
        <div class="absolute top-1/2 left-0 right-0 h-1 bg-gray-200 -translate-y-1/2 z-0"></div>
        
        <!-- Active Progress Line -->
        <div
          class="absolute top-1/2 left-0 h-1 bg-rating-green -translate-y-1/2 z-0 transition-all duration-500"
          :style="{ width: `${(Math.max(0, currentStepIndex) / (steps.length - 1)) * 100}%` }"
        ></div>

        <!-- Step Items -->
        <div
          v-for="(step, index) in steps"
          :key="step.key"
          class="relative z-10 flex flex-col items-center group"
        >
          <!-- Circular Node -->
          <div
            :class="[
              'w-9 h-9 sm:w-10 sm:h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 border-2',
              index <= currentStepIndex
                ? 'bg-rating-green border-rating-green text-white shadow-md'
                : 'bg-white border-gray-300 text-gray-400'
            ]"
          >
            <span v-if="index < currentStepIndex">✓</span>
            <span v-else>{{ step.icon }}</span>
          </div>

          <!-- Step Label -->
          <div
            :class="[
              'text-[11px] sm:text-xs font-semibold mt-2 text-center whitespace-nowrap transition',
              index <= currentStepIndex ? 'text-surface-dark font-bold' : 'text-gray-400'
            ]"
          >
            {{ step.label }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
