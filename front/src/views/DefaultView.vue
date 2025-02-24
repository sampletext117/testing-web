<template>
  <div class="layout">
    <div class="navbar">
      <Navbar />
    </div>
    <!-- <Sidebar v-if="showSidebar" /> -->
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script lang="ts" setup>
import Navbar from '@/components/Navbar.vue';
import { useRoute } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;
}

.content {
  flex: 1;
  padding: 2rem;
}

.navbar {
  width: 100%;
  display: flex;
  justify-content: center;
  border-bottom: 0.5px solid rgb(215, 215, 215);
}
</style>
