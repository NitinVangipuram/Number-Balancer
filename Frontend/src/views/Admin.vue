<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '../store/authStore';
import { useRouter } from 'vue-router';
import axios from 'axios';

const authStore = useAuthStore();
const router = useRouter();



// Game configuration data
const levels = ref([]);
const editingLevel = ref(null);
const isEditing = ref(false);
const showAddNumbers = ref(false);
const newNumberInput = ref('');

// Game-wide settings
const gameSettings = ref({
  showTimer: true,
  allowHints: true,
  hintPenalty: 5, // seconds
  soundEffects: true,
  animationSpeed: "medium", // slow, medium, fast
  saveLevelsToStorage: true
});

// Difficulty presets
const difficultyPresets = [
  { name: "Very Easy", minTarget: 5, maxTarget: 10, timeLimit: 90, numbers: [1, 2, 3, 4, 5] },
  { name: "Easy", minTarget: 10, maxTarget: 25, timeLimit: 60, numbers: [1, 2, 3, 4, 5, 6, 7] },
  { name: "Medium", minTarget: 20, maxTarget: 40, timeLimit: 45, numbers: [2, 4, 6, 8, 10, 12] },
  { name: "Hard", minTarget: 40, maxTarget: 80, timeLimit: 30, numbers: [5, 10, 15, 20, 25] },
  { name: "Very Hard", minTarget: 60, maxTarget: 120, timeLimit: 20, numbers: [7, 11, 13, 17, 19, 23] }
];

// Computed properties
const nextLevelId = computed(() => {
  return levels.value.length > 0 ? Math.max(...levels.value.map(l => l.id)) + 1 : 1;
});

const createNewLevel = () => {
  editingLevel.value = {
    id: nextLevelId.value.toString(), // Convert to string for API
    title: `Level ${nextLevelId.value}`,
    description: "New level description",
    created_by: authStore.user?.id || "admin",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    difficulty_levels: [
      {
        level_name: `Level ${nextLevelId.value}`,
        target_min: 10,
        target_max: 30,
        addends: [{ min_value: 1, max_value: 10 }],
        time_limit: 60,
        hints_available: true
      }
    ],
    starting_level: `Level ${nextLevelId.value}`,
    public: false,
    feedback_sensitivity: 1.0,
    progression_criteria: {}
  };
  isEditing.value = true;
};

const startEditLevel = (level) => {
  // Create a properly formatted editing level from the displayed level data
  editingLevel.value = {
    id: level.id.toString(),
    title: level.name,
    description: level.description || `Level ${level.id} description`,
    created_by: level.created_by || authStore.user?.id || "admin",
    created_at: level.created_at || new Date().toISOString(),
    updated_at: new Date().toISOString(),
    difficulty_levels: [
      {
        level_name: level.name,
        target_min: level.minTarget,
        target_max: level.maxTarget,
        addends: level.availableNumbers.map(num => ({ min_value: num, max_value: num })),
        time_limit: level.timeLimit,
        hints_available: true
      }
    ],
    starting_level: level.name,
    public: level.enabled,
    feedback_sensitivity: 1.0,
    progression_criteria: level.progression_criteria || {}
  };
  isEditing.value = true;
};

const cancelEdit = () => {
  editingLevel.value = null;
  isEditing.value = false;
  showAddNumbers.value = false;
  newNumberInput.value = "";
};

const saveLevel = async () => {
  if (!editingLevel.value.title || 
      !editingLevel.value.difficulty_levels[0] || 
      editingLevel.value.difficulty_levels[0].target_min >= editingLevel.value.difficulty_levels[0].target_max) {
    alert("Please ensure the level has a title and min target is less than max target");
    return;
  }

  if (!editingLevel.value.difficulty_levels[0].addends || 
      editingLevel.value.difficulty_levels[0].addends.length === 0) {
    alert("Please add at least one available number");
    return;
  }

  try {
    console.log("Sending data to backend:", editingLevel.value);
    const levelId = editingLevel.value.id;
    if (levelId && levels.value.some(l => l.id.toString() === levelId.toString())) {
      // Update existing level
      await axios.put(`https://number-balancer-l57g.vercel.app/game-configurations/${levelId}`, editingLevel.value);
    } else {
      // Add new level
      console.log("Creating new level:", editingLevel.value);
      await axios.post(`https://number-balancer-l57g.vercel.app/game-configurations/`, editingLevel.value);
    }
    await fetchGameConfigurations(); // Refresh the list
    cancelEdit();
  } catch (error) {
    console.error("Error saving level:", error.response?.data || error.message);
    alert("Failed to save level. Please check the console for details.");
  }
};

const deleteLevel = async (levelId) => {
  if (confirm("Are you sure you want to delete this level?")) {
    try {
      await axios.delete(`https://number-balancer-l57g.vercel.app/game-configurations/${levelId}`);
      await fetchGameConfigurations(); // Refresh the list
    } catch (error) {
      console.error("Error deleting level:", error.response?.data || error.message);
      alert("Failed to delete level. Please try again.");
    }
  }
};

const toggleLevelEnabled = async (level) => {
  // Create a proper API object from the displayed level
  const apiLevel = {
    id: level.id.toString(),
    title: level.name,
    description: level.description || `Level ${level.id} description`,
    created_by: level.created_by || authStore.user?.id || "admin",
    created_at: level.created_at || new Date().toISOString(),
    updated_at: new Date().toISOString(),
    difficulty_levels: [
      {
        level_name: level.name,
        target_min: level.minTarget,
        target_max: level.maxTarget,
        addends: level.availableNumbers.map(num => ({ min_value: num, max_value: num })),
        time_limit: level.timeLimit,
        hints_available: true
      }
    ],
    starting_level: level.name,
    public: !level.enabled, // Toggle the enabled state
    feedback_sensitivity: 1.0,
    progression_criteria: level.progression_criteria || {}
  };

  try {
    await axios.put(`https://number-balancer-l57g.vercel.app/game-configurations/${level.id}`, apiLevel);
    // Update the local state after successful API call
    level.enabled = !level.enabled;
  } catch (error) {
    console.error("Error toggling level:", error.response?.data || error.message);
    alert("Failed to toggle level. Please try again.");
  }
};

const addNumberToLevel = () => {
  const num = parseInt(newNumberInput.value);
  if (!isNaN(num) && num > 0) {
    // Initialize addends array if it doesn't exist
    if (!editingLevel.value.difficulty_levels[0].addends) {
      editingLevel.value.difficulty_levels[0].addends = [];
    }
    
    // Check if the number already exists
    if (!editingLevel.value.difficulty_levels[0].addends.some(addend => 
        addend.min_value === num && addend.max_value === num)) {
      editingLevel.value.difficulty_levels[0].addends.push({ min_value: num, max_value: num });
      editingLevel.value.difficulty_levels[0].addends.sort((a, b) => a.min_value - b.min_value);
    }
    newNumberInput.value = "";
  }
};

const removeNumberFromLevel = (number) => {
  editingLevel.value.difficulty_levels[0].addends = 
    editingLevel.value.difficulty_levels[0].addends.filter(addend => 
      !(addend.min_value === number && addend.max_value === number));
};

const applyDifficultyPreset = (preset) => {
  if (!editingLevel.value) return;
  editingLevel.value.difficulty_levels[0].target_min = preset.minTarget;
  editingLevel.value.difficulty_levels[0].target_max = preset.maxTarget;
  editingLevel.value.difficulty_levels[0].time_limit = preset.timeLimit;
  editingLevel.value.difficulty_levels[0].addends = preset.numbers.map(num => ({ min_value: num, max_value: num }));
};

const exportConfig = () => {
  const dataStr = JSON.stringify(levels.value, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
  const exportFileDefaultName = 'balance-game-config.json';

  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
};

const importConfig = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedLevels = JSON.parse(e.target.result);
        if (Array.isArray(importedLevels)) {
          levels.value = importedLevels;
          alert("Configuration imported successfully!");
        } else {
          alert("Invalid configuration format. Expected an array.");
        }
      } catch (error) {
        console.error("Error parsing imported file:", error);
        alert("Failed to import configuration. Invalid JSON format.");
      }
    };
    reader.readAsText(file);
  }
};

const resetToDefaults = () => {
  if (confirm("Are you sure you want to reset all settings to defaults? This cannot be undone.")) {
    gameSettings.value = {
      showTimer: true,
      allowHints: true,
      hintPenalty: 5,
      soundEffects: true,
      animationSpeed: "medium",
      saveLevelsToStorage: true
    };
    alert("Settings reset to defaults.");
  }
};

const fetchGameConfigurations = async () => {
  try {
    const response = await axios.get(`https://number-balancer-l57g.vercel.app/game-configurations/`);
    // Transform API data to the format expected by the frontend
    levels.value = response.data.map(item => {
      const difficulty = item.difficulty_levels[0] || {};
      return {
        id: item.id,
        name: item.title,
        description: item.description,
        minTarget: difficulty.target_min || 0,
        maxTarget: difficulty.target_max || 100,
        timeLimit: difficulty.time_limit || 60,
        // Extract available numbers from addends
        availableNumbers: (difficulty.addends || [])
          .map(addend => {
            // If min_value equals max_value, it's a single number
            if (addend.min_value === addend.max_value) return addend.min_value;
            // Otherwise, return null and filter it out
            return null;
          })
          .filter(num => num !== null),
        enabled: item.public,
        created_by: item.created_by,
        created_at: item.created_at,
        updated_at: item.updated_at,
        progression_criteria: item.progression_criteria || {}
      };
    });
  } catch (error) {
    console.error("Error fetching game configurations:", error.response?.data || error.message);
    alert("Failed to load game configurations. Please check the console for details.");
  }
};

// Lifecycle hooks
onMounted(async () => {
  try {
    await authStore.fetchUser(); // Ensure role is loaded before checking
    if (!authStore.user || authStore.role !== "admin") {
      router.push("/dashboard");
    } else {
      await fetchGameConfigurations();
    }
  } catch (error) {
    console.error("Error fetching user:", error.response?.data || error.message);
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
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-6">Balance Game Admin Panel</h1>
    
    <div v-if="authStore.isLoading" class="text-center p-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
      <p class="mt-2">Loading...</p>
    </div>
    
    <div v-else-if="authStore.role !== 'admin'" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6">
      <p>You do not have admin access.</p>
    </div>
    
    <div v-else>
      <!-- Main admin panel content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Left column: Level list -->
        <div class="lg:col-span-2 bg-white p-4 rounded-lg shadow">
          <div class="flex justify-between mb-4">
            <h2 class="text-xl font-bold">Game Levels</h2>
            <button 
              @click="createNewLevel" 
              class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Add New Level
            </button>
          </div>
          
          <div class="overflow-x-auto">
            <table class="min-w-full bg-white">
              <thead>
                <tr class="bg-gray-100">
                  <th class="py-2 px-4 text-left">ID</th>
                  <th class="py-2 px-4 text-left">Name</th>
                  <th class="py-2 px-4 text-left">Target Range</th>
                  <th class="py-2 px-4 text-left">Numbers</th>
                  <th class="py-2 px-4 text-left">Time</th>
                  <th class="py-2 px-4 text-left">Status</th>
                  <th class="py-2 px-4 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="level in levels" :key="level.id" class="border-t">
                  <td class="py-2 px-4">{{ level.id }}</td>
                  <td class="py-2 px-4">{{ level.name }}</td>
                  <td class="py-2 px-4">{{ level.minTarget }} - {{ level.maxTarget }}</td>
                  <td class="py-2 px-4">
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-for="num in level.availableNumbers"
                        :key="num" 
                        class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                      >
                        {{ num }}
                      </span>
                    </div>
                  </td>
                  <td class="py-2 px-4">{{ level.timeLimit }}s</td>
                  <td class="py-2 px-4">
                    <span 
                      :class="level.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" 
                      class="text-xs px-2 py-1 rounded"
                    >
                      {{ level.enabled ? 'Active' : 'Disabled' }}
                    </span>
                  </td>
                  <td class="py-2 px-4">
                    <div class="flex space-x-2">
                      <button 
                        @click="startEditLevel(level)" 
                        class="px-2 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                      >
                        Edit
                      </button>
                      <button 
                        @click="toggleLevelEnabled(level)" 
                        class="px-2 py-1 text-sm rounded"
                        :class="level.enabled ? 'bg-yellow-500 hover:bg-yellow-600 text-white' : 'bg-green-500 hover:bg-green-600 text-white'"
                      >
                        {{ level.enabled ? 'Disable' : 'Enable' }}
                      </button>
                      <button 
                        @click="deleteLevel(level.id)" 
                        class="px-2 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Right column: Game settings -->
        <div class="bg-white p-4 rounded-lg shadow">
          <h2 class="text-xl font-bold mb-4">Game Settings</h2>
          
          <div class="space-y-4">
            <div>
              <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" v-model="gameSettings.showTimer" class="form-checkbox h-5 w-5 text-blue-600">
                <span>Show Timer</span>
              </label>
            </div>
            
            <div>
              <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" v-model="gameSettings.allowHints" class="form-checkbox h-5 w-5 text-blue-600">
                <span>Allow Hints</span>
              </label>
            </div>
            
            <div v-if="gameSettings.allowHints">
              <label class="block text-sm font-medium text-gray-700 mb-1">Hint Time Penalty (seconds)</label>
              <input 
                type="number" 
                v-model.number="gameSettings.hintPenalty" 
                min="0" 
                max="30"
                class="w-full p-2 border rounded"
              >
            </div>
            
            <div>
              <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" v-model="gameSettings.soundEffects" class="form-checkbox h-5 w-5 text-blue-600">
                <span>Sound Effects</span>
              </label>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Animation Speed</label>
              <select v-model="gameSettings.animationSpeed" class="w-full p-2 border rounded">
                <option value="slow">Slow</option>
                <option value="medium">Medium</option>
                <option value="fast">Fast</option>
              </select>
            </div>
            
            <div>
              <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" v-model="gameSettings.saveLevelsToStorage" class="form-checkbox h-5 w-5 text-blue-600">
                <span>Save Changes to Local Storage</span>
              </label>
            </div>
            
            <div class="pt-4 space-y-2">
              <h3 class="font-medium">Import/Export</h3>
              <div class="flex space-x-2">
                <button 
                  @click="exportConfig" 
                  class="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                >
                  Export Configuration
                </button>
                
                <label class="px-3 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 cursor-pointer text-sm">
                  Import Configuration
                  <input 
                    type="file" 
                    @change="importConfig" 
                    accept=".json" 
                    class="hidden"
                  >
                </label>
              </div>
              
              <button 
                @click="resetToDefaults" 
                class="w-full px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm mt-4"
              >
                Reset to Defaults
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Level Edit Modal -->
      <div v-if="isEditing" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-screen overflow-y-auto">
          <div class="p-6">
            <h2 class="text-xl font-bold mb-4">
              {{ editingLevel && editingLevel.id ? `Edit Level: ${editingLevel.title}` : 'Create New Level' }}
            </h2>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Level Id</label>
                <input 
                  type="text" 
                  v-model="editingLevel.id" 
                  class="w-full p-2 border rounded"
                  placeholder="Level name"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Level Name</label>
                <input 
                  type="text" 
                  v-model="editingLevel.title" 
                  class="w-full p-2 border rounded"
                  placeholder="Level name"
                >
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Min Target Value</label>
                  <input 
                    type="number" 
                    v-model.number="editingLevel.difficulty_levels[0].target_min" 
                    min="1" 
                    class="w-full p-2 border rounded"
                  >
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Max Target Value</label>
                  <input 
                    type="number" 
                    v-model.number="editingLevel.difficulty_levels[0].target_max" 
                    min="1" 
                    class="w-full p-2 border rounded"
                  >
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Time Limit (seconds)</label>
                <input 
                  type="number" 
                  v-model.number="editingLevel.difficulty_levels[0].time_limit" 
                  min="5" 
                  max="300"
                  class="w-full p-2 border rounded"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Available Numbers</label>
                <div class="flex flex-wrap gap-2 p-2 border rounded bg-gray-50 min-h-12">
                  
                  
                  <div v-if="!showAddNumbers" @click="showAddNumbers = true" class="cursor-pointer text-blue-500 px-2 py-1">
                    + Add Number
                  </div>
                  
                  <div v-if="showAddNumbers" class="flex items-center space-x-2">
                    <input 
                      type="number" 
                      v-model="newNumberInput" 
                      min="1" 
                      class="w-20 p-1 border rounded"
                      @keyup.enter="addNumberToLevel"
                    >
                    <button 
                      @click="addNumberToLevel" 
                      class="bg-blue-500 text-white px-2 py-1 rounded text-xs"
                    >
                      Add
                    </button>
                    <button 
                      @click="showAddNumbers = false" 
                      class="text-gray-500 text-xs"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
              
              <div>
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" v-model="editingLevel.public" class="form-checkbox h-5 w-5 text-blue-600">
                  <span>Level Enabled</span>
                </label>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Apply Difficulty Preset</label>
                <div class="flex flex-wrap gap-2">
                  <button 
                    v-for="preset in difficultyPresets" 
                    :key="preset.name"
                    @click="applyDifficultyPreset(preset)"
                    class="px-2 py-1 bg-gray-200 rounded text-sm hover:bg-gray-300"
                  >
                    {{ preset.name }}
                  </button>
                </div>
                <p class="text-xs text-gray-500 mt-1">Applying a preset will change numbers, targets and time limit.</p>
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 mt-6">
              <button 
                @click="cancelEdit" 
                class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
              <button 
                @click="saveLevel" 
                class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Save Level
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Add your custom styles here */
</style>