<template>
    <div class="relative">
      <input
        type="number"
        v-model.number="inputValue"
        :disabled="isBalanced"
        class="w-16 h-16 text-center text-xl font-bold rounded-lg transition-colors duration-300 focus:outline-none focus:ring-2"
        :class="[
          isBalanced 
            ? 'bg-green-200 text-green-800 cursor-not-allowed' 
            : 'bg-white text-slate-800 focus:ring-blue-400'
        ]"
        min="0"
        :max="maxValue"
        @input="onInput"
      />
      <button 
        v-if="modelValue && !isBalanced" 
        @click="clearInput"
        class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400"
      >
        ×
      </button>
    </div>
  </template>
  
  <script setup lang="ts">
  import { computed } from 'vue';
  import { DIFFICULTY_RANGES } from '@/constants/gameconstant';
  
  const props = defineProps<{
    modelValue: number;
    isBalanced: boolean;
    index: number;
  }>();
  
  const emit = defineEmits<{
    (e: 'update:modelValue', value: number): void;
    (e: 'input'): void;
  }>();
  
  const inputValue = computed({
    get: () => props.modelValue,
    set: (value: number) => {
      emit('update:modelValue', value);
    }
  });
  
  const maxValue = computed(() => DIFFICULTY_RANGES.hard.max);
  
  function onInput() {
    emit('input');
  }
  
  function clearInput() {
    emit('update:modelValue', 0);
    emit('input');
  }
  </script>