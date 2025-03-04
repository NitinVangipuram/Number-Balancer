<template>
    <div 
      class="absolute top-32 left-1/2 transform -translate-x-1/2 w-4/5 h-3 transition-transform duration-500 ease-in-out"
      :class="[isBalanced ? 'bg-green-600' : 'bg-slate-700']"
      :style="{ transform: `translateX(-50%) rotate(${tiltAngle}deg)` }"
    >
      <slot></slot>
    </div>
  </template>
  
  <script setup lang="ts">
  defineProps<{
    tiltAngle: number;
    isBalanced: boolean;
  }>();
  </script>