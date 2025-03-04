<template>
    <div class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Difficulty Level -->
        <div>
          <label class="block text-slate-700 font-medium mb-2">Difficulty Level</label>
          <select 
            v-model="modelValue.difficulty"
            class="w-full p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            @change="emitUpdate"
          >
            <option value="easy">Easy (1-10)</option>
            <option value="medium">Medium (1-20)</option>
            <option value="hard">Hard (1-50)</option>
          </select>
        </div>
  
        <!-- Number of Addends -->
        <div>
          <label class="block text-slate-700 font-medium mb-2">Number of Addends</label>
          <div class="flex items-center">
            <input 
              type="range" 
              v-model.number="modelValue.numberofAddends" 
              min="1" 
              max="5" 
              class="w-full mr-4"
              @change="emitUpdate"
            />
            <span class="text-slate-700 font-medium">{{ modelValue.numberofAddends }}</span>
          </div>
        </div>
      </div>
  
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Min Target Value -->
        <div>
          <label class="block text-slate-700 font-medium mb-2">Min Target Value</label>
          <input 
            type="number" 
            v-model.number="modelValue.minTarget" 
            class="w-full p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            min="1"
            @change="emitUpdate"
          />
        </div>
  
        <!-- Max Target Value -->
        <div>
          <label class="block text-slate-700 font-medium mb-2">Max Target Value</label>
          <input 
            type="number" 
            v-model.number="modelValue.maxTarget" 
            class="w-full p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            :min="modelValue.minTarget + 5"
            @change="emitUpdate"
          />
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { computed } from 'vue';
  import type { GameSettings } from '@/types/gametypes';
  
  const props = defineProps<{
    settings: GameSettings;
  }>();
  
  const emit = defineEmits<{
    (e: 'update:settings', settings: GameSettings): void;
  }>();
  
  const modelValue = computed({
    get: () => props.settings,
    set: (value: GameSettings) => {
      emit('update:settings', value);
    }
  });
  
  function emitUpdate() {
    emit('update:settings', modelValue.value);
  }
  </script>
  