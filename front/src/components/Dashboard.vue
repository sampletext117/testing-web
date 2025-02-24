<template>
<div></div>
</template>

<script lang="ts" setup>
import { useAuthStore } from '@/stores/auth-store';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const role = authStore.tokenData?.role;

if (role === 'admin') {
  router.push({
    path: '/admin',
  });
} else if (role === 'candidate') {
  router.push({
    path: '/candidate',
  })
} else {
  router.push({
    path: '/elections',
  })
}

</script>

<style scoped></style>
