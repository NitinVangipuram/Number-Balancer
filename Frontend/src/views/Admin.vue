<script setup>
import { useAuthStore } from "../store/authStore";
import { useRouter } from "vue-router";
import { onMounted, watch } from "vue";

const authStore = useAuthStore();
const router = useRouter();

onMounted(async () => {
  try {
    await authStore.fetchUser(); // Ensure role is loaded before checking

    console.log("User Role:", authStore.role); // Debugging Output

    if (!authStore.user || authStore.role !== "admin") {
      router.push("/dashboard"); 
    }
  } catch (error) {
    console.error("Error fetching user:", error);
  }
});

// Watch for changes in user role and redirect dynamically
watch(() => authStore.role, (newRole) => {
  if (newRole !== "admin") {
    router.push("/dashboard");
  }
});
</script>

<template>
  <div>
    <h1>Admin Panel</h1>
    <p v-if="authStore.isLoading">Loading...</p>
    <p v-else-if="authStore.role === 'admin'">Welcome, Admin!</p>
    <p v-else>You do not have access.</p>
  </div>
</template>
