<template>
    <div 
      class="text-center py-4 px-6 rounded-lg text-lg font-medium mb-4 transition-colors duration-300"
      :class="classObject"
    >
      {{ message }}
    </div>
  </template>
  
  <script setup lang="ts">
  defineProps<{
    message: string;
    classObject: Record<string, boolean>;
  }>();
  </script>
