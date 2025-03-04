<script setup>
import { useAuthStore } from "../store/authStore";
import { useRouter } from "vue-router";
import { onMounted, watch, ref, computed } from "vue";

const authStore = useAuthStore();
const router = useRouter();

// Game configuration data
const levels = ref([
  { 
    id: 1, 
    name: "Level 1 - Beginner", 
    minTarget: 5, 
    maxTarget: 15, 
    availableNumbers: [1, 2, 3, 4, 5],
    timeLimit: 60, // seconds
    enabled: true
  },
  { 
    id: 2, 
    name: "Level 2 - Easy", 
    minTarget: 10, 
    maxTarget: 25, 
    availableNumbers: [1, 2, 3, 4, 5, 6, 7],
    timeLimit: 45, // seconds
    enabled: true
  },
  { 
    id: 3, 
    name: "Level 3 - Intermediate", 
    minTarget: 15, 
    maxTarget: 40, 
    availableNumbers: [2, 4, 6, 8, 10, 12],
    timeLimit: 40, // seconds
    enabled: true
  },
  { 
    id: 4, 
    name: "Level 4 - Advanced", 
    minTarget: 30, 
    maxTarget: 60, 
    availableNumbers: [5, 10, 15, 20, 25],
    timeLimit: 30, // seconds
    enabled: true
  },
  { 
    id: 5, 
    name: "Level 5 - Expert", 
    minTarget: 50, 
    maxTarget: 100, 
    availableNumbers: [5, 7, 9, 11, 13, 17, 19],
    timeLimit: 25, // seconds
    enabled: false
  }
]);

// For creating/editing a level
const editingLevel = ref(null);
const isEditing = ref(false);
const showAddNumbers = ref(false);
const newNumberInput = ref("");

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

// Methods
const startEditLevel = (level) => {
  editingLevel.value = JSON.parse(JSON.stringify(level)); // Create a deep copy
  isEditing.value = true;
};

const createNewLevel = () => {
  editingLevel.value = {
    id: nextLevelId.value,
    name: `Level ${nextLevelId.value}`,
    minTarget: 10,
    maxTarget: 30,
    availableNumbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    timeLimit: 60,
    enabled: true
  };
  isEditing.value = true;
};

const cancelEdit = () => {
  editingLevel.value = null;
  isEditing.value = false;
  showAddNumbers.value = false;
  newNumberInput.value = "";
};

const saveLevel = () => {
  if (!editingLevel.value.name || editingLevel.value.minTarget >= editingLevel.value.maxTarget) {
    alert("Please ensure the level has a name and min target is less than max target");
    return;
  }

  if (editingLevel.value.availableNumbers.length === 0) {
    alert("Please add at least one available number");
    return;
  }

  const index = levels.value.findIndex(l => l.id === editingLevel.value.id);
  if (index >= 0) {
    // Update existing level
    levels.value[index] = { ...editingLevel.value };
  } else {
    // Add new level
    levels.value.push({ ...editingLevel.value });
  }

  // Sort levels by ID
  levels.value.sort((a, b) => a.id - b.id);
  
  saveChangesToStorage();
  cancelEdit();
};

const deleteLevel = (levelId) => {
  if (confirm("Are you sure you want to delete this level?")) {
    levels.value = levels.value.filter(level => level.id !== levelId);
    saveChangesToStorage();
  }
};

const toggleLevelEnabled = (level) => {
  level.enabled = !level.enabled;
  saveChangesToStorage();
};

const addNumberToLevel = () => {
  const num = parseInt(newNumberInput.value);
  if (!isNaN(num) && num > 0) {
    if (!editingLevel.value.availableNumbers.includes(num)) {
      editingLevel.value.availableNumbers.push(num);
      editingLevel.value.availableNumbers.sort((a, b) => a - b);
    }
    newNumberInput.value = "";
  }
};

const removeNumberFromLevel = (number) => {
  editingLevel.value.availableNumbers = editingLevel.value.availableNumbers.filter(n => n !== number);
};

const applyDifficultyPreset = (preset) => {
  if (!editingLevel.value) return;
  
  editingLevel.value.minTarget = preset.minTarget;
  editingLevel.value.maxTarget = preset.maxTarget;
  editingLevel.value.timeLimit = preset.timeLimit;
  editingLevel.value.availableNumbers = [...preset.numbers];
};

const saveChangesToStorage = () => {
  if (gameSettings.value.saveLevelsToStorage) {
    localStorage.setItem('balanceGameLevels', JSON.stringify(levels.value));
    localStorage.setItem('balanceGameSettings', JSON.stringify(gameSettings.value));
  }
};

const loadFromStorage = () => {
  const storedLevels = localStorage.getItem('balanceGameLevels');
  const storedSettings = localStorage.getItem('balanceGameSettings');
  
  if (storedLevels) {
    levels.value = JSON.parse(storedLevels);
  }
  
  if (storedSettings) {
    gameSettings.value = JSON.parse(storedSettings);
  }
};

const resetToDefaults = () => {
  if (confirm("Are you sure you want to reset all levels and settings to default values? This cannot be undone.")) {
    localStorage.removeItem('balanceGameLevels');
    localStorage.removeItem('balanceGameSettings');
    // Reload the page to reset all values
    window.location.reload();
  }
};

const exportConfig = () => {
  const config = {
    levels: levels.value,
    settings: gameSettings.value,
    exportDate: new Date().toISOString()
  };
  
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = `balance-game-config-${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

const importConfig = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const config = JSON.parse(e.target.result);
      if (config.levels && Array.isArray(config.levels)) {
        levels.value = config.levels;
      }
      if (config.settings) {
        gameSettings.value = config.settings;
      }
      saveChangesToStorage();
      alert("Configuration imported successfully!");
    } catch (error) {
      alert("Error importing configuration: " + error.message);
    }
  };
  reader.readAsText(file);
  event.target.value = null; // Reset input
};

// Lifecycle hooks
onMounted(async () => {
  try {
    await authStore.fetchUser(); // Ensure role is loaded before checking
    console.log("User Role:", authStore.role); // Debugging Output
    if (!authStore.user || authStore.role !== "admin") {
      router.push("/dashboard"); 
    } else {
      loadFromStorage();
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

// Save settings when they change
watch(gameSettings, () => {
  saveChangesToStorage();
}, { deep: true });
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
                        v-for="num in level.availableNumbers.slice(0, 5)" 
                        :key="num" 
                        class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                      >
                        {{ num }}
                      </span>
                      <span 
                        v-if="level.availableNumbers.length > 5" 
                        class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded"
                      >
                        +{{ level.availableNumbers.length - 5 }} more
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
              {{ editingLevel.id ? `Edit Level: ${editingLevel.name}` : 'Create New Level' }}
            </h2>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Level Name</label>
                <input 
                  type="text" 
                  v-model="editingLevel.name" 
                  class="w-full p-2 border rounded"
                  placeholder="Level name"
                >
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Min Target Value</label>
                  <input 
                    type="number" 
                    v-model.number="editingLevel.minTarget" 
                    min="1" 
                    class="w-full p-2 border rounded"
                  >
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Max Target Value</label>
                  <input 
                    type="number" 
                    v-model.number="editingLevel.maxTarget" 
                    min="1" 
                    class="w-full p-2 border rounded"
                  >
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Time Limit (seconds)</label>
                <input 
                  type="number" 
                  v-model.number="editingLevel.timeLimit" 
                  min="5" 
                  max="300"
                  class="w-full p-2 border rounded"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Available Numbers</label>
                <div class="flex flex-wrap gap-2 p-2 border rounded bg-gray-50 min-h-12">
                  <div 
                    v-for="num in editingLevel.availableNumbers" 
                    :key="num"
                    class="flex items-center bg-blue-100 text-blue-800 px-2 py-1 rounded"
                  >
                    {{ num }}
                    <button 
                      @click="removeNumberFromLevel(num)" 
                      class="ml-1 text-blue-500 hover:text-blue-700"
                    >
                      &times;
                    </button>
                  </div>
                  
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
                  <input type="checkbox" v-model="editingLevel.enabled" class="form-checkbox h-5 w-5 text-blue-600">
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