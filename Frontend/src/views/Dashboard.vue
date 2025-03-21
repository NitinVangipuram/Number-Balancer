<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <div class="logo-container">
        <img src="../beach-ball_375219.png" alt="Logo" class="logo" />
      </div>
      <div class="user-menu">
        <span>{{ userEmail }}</span>
        <button @click="logout" class="logout-button">Logout</button>
      </div>
    </header>
    
    <main class="dashboard-content">
      <h1 class="dashboard-title">Math Balance Game</h1>
      
      <!-- Balance Scale Game Component -->
      <div class="game-container">
        <BalanceScale :settings="gameSettings" @saveGame="saveGameState" />
      </div>
      
      <!-- Game Instructions -->
      <div class="dashboard-card">
        <h2>How to Play</h2>
        <p>Balance the scale by placing numbers on both sides to make them equal. Drag and drop numbers to find the correct mathematical balance!</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getAuth, onAuthStateChanged, signOut } from "firebase/auth";
import BalanceScale from "../components/game/BalanceScale.vue";
import axios from "axios";

const auth = getAuth();
const router = useRouter();
const userEmail = ref("");
const gameSettings = ref({ minTarget: 10, maxTarget: 100, numberOfAddends: 3 });

onMounted(async () => {
  onAuthStateChanged(auth, async (user) => {
    if (user) {
      userEmail.value = user.email || "User";
    } else {
      router.push("/signin");
    }
  });
});

const logout = async () => {
  try {
    await signOut(auth);
    router.push("/signin"); // Redirect to login after logout
  } catch (error: any) {
    console.error("Logout failed:", error.message);
  }
};

const saveGameState = async (gameState: any) => {
  try {
    const token = await auth.currentUser.getIdToken();
    await axios.post("https://number-balancer-l57g.vercel.app/save-game", gameState, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error) {
    console.error("Failed to save game state:", error);
  }
};
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  height: 40px;
  width: auto;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-menu span {
  font-weight: 500;
  color: #333;
}

.logout-button {
  padding: 8px 16px;
  background-color: #f3f4f6;
  color: #333;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #e5e7eb;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.dashboard-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.game-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  padding: 25px;
  margin-bottom: 30px;
}

.dashboard-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 20px;
  width: 100%;
  max-width: 800px;
}

.dashboard-card h2 {
  font-size: 20px;
  color: #333;
  margin-bottom: 15px;
}

.dashboard-card p {
  color: #666;
  line-height: 1.6;
}
</style>