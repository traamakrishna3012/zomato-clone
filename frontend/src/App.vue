<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import Navbar from './components/Navbar.vue'
import AuthModal from './components/AuthModal.vue'
import CartDrawer from './components/CartDrawer.vue'
import MismatchModal from './components/MismatchModal.vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.loadUserFromStorage()
})
</script>

<template>
  <div id="app" class="min-h-screen bg-bg-gray flex flex-col font-sans antialiased text-surface-dark">
    <!-- Main Top Navigation -->
    <Navbar />

    <!-- Routed Page View -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full">
      <RouterView />
    </main>

    <!-- Global Floating / Modal Overlays -->
    <CartDrawer />
    <MismatchModal />
    <AuthModal />
  </div>
</template>
