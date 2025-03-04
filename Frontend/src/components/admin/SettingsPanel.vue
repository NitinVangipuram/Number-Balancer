<template>
    <div class="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto mb-8">
      <h2 class="text-2xl font-bold text-slate-800 mb-6">Game Settings</h2>
      
      <SettingsForm
        :settings="localSettings"
        @update:settings="updateSettings"
      />
  
      <button 
        @click="applySettings"
        class="mt-6 w-full bg-green-500 text-white py-3 px-6 rounded-lg font-medium 
               transition-colors duration-300 hover:bg-green-600 focus:outline-none focus:ring-2 
               focus:ring-green-400"
      >
        Apply Settings
      </button>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import type { GameSettings } from '@/types/gametypes';
  import { DEFAULT_SETTING } from '@/constants/gameconstant';
  import SettingsForm from './SettingsForm.vue';
  
  const emit = defineEmits<{
    (e: 'update:settings', settings: GameSettings): void;
  }>();
  
  const localSettings = ref<GameSettings>({ ...DEFAULT_SETTING });
  
  function updateSettings(settings: GameSettings) {
    localSettings.value = settings;
  }
  
  function applySettings() {
    emit('update:settings', localSettings.value);
  }
  </script>
  