<template>
    <div 
      class="flex items-center justify-center w-32 h-32 rounded-full shadow-lg transition-colors duration-300"
      :class="[baseClass, isBalanced ? 'bg-green-500' : 'bg-blue-500']"
    >
      <slot></slot>
    </div>
  </template>
  
  <script setup lang="ts">
  defineProps<{
    isBalanced: boolean;
    baseClass: string;
  }>();
  </script>