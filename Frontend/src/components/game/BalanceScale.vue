<template>
  <div class="flex flex-col items-center w-full max-w-4xl mx-auto p-4">
    <!-- Level Selection -->
    <div class="mt-4 mb-6">
      <div class="text-lg font-semibold mb-2">Select Level:</div>
      <div class="flex flex-wrap gap-2 justify-center">
        <button 
          v-for="level in levels" 
          :key="level.id"
          @click="selectLevel(level)"
          class="w-32 h-12 rounded-md flex items-center justify-center text-xl font-bold transition bg-gray-200 hover:bg-gray-300 cursor-pointer"
        >
          {{ level.title }}
        </button>
      </div>
    </div>

    <!-- Existing template content -->
    <div class="relative w-full h-[400px] mb-8">
      <!-- Fulcrum -->
      <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-6 h-40 bg-slate-700"></div>
      
      <!-- Main Beam -->
      <ScaleBeam :tilt-angle="tiltAngle" :is-balanced="isBalanced">
        <!-- Left Pan -->
        <ScalePan 
          :is-balanced="isBalanced"
          base-class="absolute left-0 -translate-x-1/2 -translate-y-1/2"
        >
          <span class="text-3xl font-bold text-white">{{ target }}</span>
        </ScalePan>

        <!-- Right Pan -->
        <ScalePan 
          :is-balanced="isBalanced"
          base-class="absolute right-0 translate-x-1/2 -translate-y-1/2"
        >
          <!-- Added max-height and overflow-y-auto to make it scrollable -->
          <div class="flex flex-wrap justify-center gap-2 w-32 max-h-40 overflow-y-auto p-2 bg-white/10 rounded">
            <!-- Number blocks that have been added -->
            <div 
              v-for="(value, index) in selectedBlocks" 
              :key="'selected-' + index"
              class="w-10 h-10 flex items-center justify-center rounded-md cursor-pointer transition-all"
              :class="isBalanced ? 'bg-green-500 text-white' : 'bg-blue-500 text-white'"
              @click="removeBlock(index)"
            >
              {{ value }}
            </div>
            
            <!-- Placeholder if no blocks added -->
            <div 
              v-if="selectedBlocks.length === 0" 
              class="w-full text-center text-gray-500"
            >
              Add numbers below
            </div>
          </div>
        </ScalePan>
      </ScaleBeam>
    </div>

    <!-- Number Selection -->
    <div class="mt-4 mb-6">
      <div class="text-lg font-semibold mb-2">Available Number Blocks:</div>
      <div class="flex flex-wrap gap-2 justify-center">
        <button 
          v-for="num in availableNumbers" 
          :key="num"
          @click="addBlock(num)"
          class="w-12 h-12 rounded-md flex items-center justify-center text-xl font-bold transition"
          :class="[
            isBalanced 
              ? 'bg-gray-300 cursor-not-allowed' 
              : 'bg-gray-200 hover:bg-gray-300 cursor-pointer'
          ]"
          :disabled="isBalanced"
        >
          {{ num }}
        </button>
      </div>
    </div>

    <!-- Current Sum Display -->
    <div class="p-4 bg-gray-100 rounded-lg mb-4">
      <div class="text-center">
        <span class="text-lg">Current Sum: </span>
        <span class="text-2xl font-bold">{{ currentSum }}</span>
      </div>
    </div>

    <!-- Timer Display -->
    <div class="p-4 bg-gray-100 rounded-lg mb-4">
      <div class="text-center">
        <span class="text-lg">Time Remaining: </span>
        <span class="text-2xl font-bold">{{ timeRemaining }}s</span>
      </div>
    </div>

    <!-- Feedback -->
    <FeedbackMessage 
      :message="feedbackMessage"
      :class-object="feedbackClass"
    />
    
    <!-- Game Controls -->
    <div class="flex gap-4 mt-4">
      <button 
        @click="generateTarget" 
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
      >
        New Target
      </button>
      
      <button 
        @click="resetGame" 
        class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
      >
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import ScaleBeam from './ScaleBeam.vue';
import ScalePan from './ScalePan.vue';
import FeedbackMessage from './FeedbackMessage.vue';
import axios from "axios";
const props = defineProps({
  settings: {
    type: Object,
    required: true
  }
});

// Game state
const target = ref(0);
const selectedBlocks = ref([]);
const tiltAngle = ref(0);
const isBalanced = ref(false);
const feedbackMessage = ref('Add number blocks to reach the target!');
const levels = ref([]);
const selectedLevel = ref(null);
const timeRemaining = ref(0);
let timerInterval = null;

// Available numbers to choose from (1-10)
const availableNumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Calculate the current sum of all selected blocks
const currentSum = computed(() => {
  return selectedBlocks.value.reduce((sum, value) => sum + value, 0);
});

// Calculate feedback class based on game state
const feedbackClass = computed(() => {
  if (isBalanced.value) {
    return {
      'text-green-500': true,
      'font-bold': true
    };
  }
  
  const difference = currentSum.value - target.value;
  
  if (difference > 0) {
    return {
      'text-yellow-500': true,
      'font-bold': true
    };
  } else if (difference < 0) {
    return {
      'text-blue-500': true,
      'font-bold': true
    };
  }
  
  return {
    'text-gray-700': true
  };
});

// Fetch levels from the API
const fetchLevels = async () => {
  const response = await axios.get("http://127.0.0.1:8000/game-configurations");
  levels.value = response.data;
};

// Select a level
const selectLevel = (level) => {
  selectedLevel.value = level;
  generateTarget();
  startTimer();
};

// Generate a new target value within the min/max range
const generateTarget = () => {
  if (selectedLevel.value) {
    const min = selectedLevel.value.difficulty_levels[0].target_min || 10;
    const max = selectedLevel.value.difficulty_levels[0].target_max || 30;
    target.value = Math.floor(Math.random() * (max - min + 1)) + min;
    
    // Reset selected blocks
    selectedBlocks.value = [];
    
    // Reset tilt
    calculateTilt();
  }
};

// Add a number block to the pan
const addBlock = (num) => {
  if (!isBalanced.value) {
    selectedBlocks.value.push(num);
    calculateTilt();
  }
};

// Remove a number block from the pan - now works regardless of balance state
const removeBlock = (index) => {
  selectedBlocks.value.splice(index, 1);
  calculateTilt();
};

// Calculate the tilt angle based on the difference between target and currentSum
const calculateTilt = () => {
  const difference = currentSum.value - target.value;
  
  // Check if balanced
  if (difference === 0 && currentSum.value > 0) {
    isBalanced.value = true;
    tiltAngle.value = 0;
    feedbackMessage.value = 'Perfect balance! You made ' + target.value + '! 🎉';
  } else {
    isBalanced.value = false;
    
    // Calculate tilt angle (max ±20 degrees)
    const maxTilt = 20;
    const tiltFactor = Math.min(Math.abs(difference) / target.value, 1);
    tiltAngle.value = Math.sign(difference) * tiltFactor * maxTilt;
    
    // Update feedback message
    if (difference === 0 && currentSum.value === 0) {
      feedbackMessage.value = 'Add number blocks to reach the target!';
    } else if (difference > 0) {
      feedbackMessage.value = 'Too much! Your sum is greater than the target.';
    } else {
      feedbackMessage.value = 'Not enough! Add more blocks to reach the target.';
    }
  }
};

// Reset the game (clear blocks but keep the same target)
const resetGame = () => {
  selectedBlocks.value = [];
  isBalanced.value = false;
  calculateTilt();
  startTimer();
};

// Start the timer
const startTimer = () => {
  if (selectedLevel.value) {
    timeRemaining.value = selectedLevel.value.difficulty_levels[0].time_limit || 60;
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      if (timeRemaining.value > 0) {
        timeRemaining.value--;
      } else {
        clearInterval(timerInterval);
        feedbackMessage.value = 'Time is up! Try again.';
      }
    }, 1000);
  }
};

// Watch for changes in settings
watch(() => props.settings, () => {
  generateTarget();
}, { deep: true });

// Initialize the game on mount
onMounted(() => {
  fetchLevels();
});
</script>
