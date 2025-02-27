import { createRouter, createWebHistory } from "vue-router";
import Signup from "../views/Signup.vue";
import Signin from "../views/Signin.vue";
import Dashboard from "../views/Dashboard.vue";
import Admin from "@/views/Admin.vue";
import { getAuth, onAuthStateChanged} from "firebase/auth";
import firebase from "@/firebase";
import { useAuthStore } from "@/store/authStore";


const auth = getAuth(firebase);

const routes = [
  { path: "/signup", component: Signup },
  { path: "/signin", component: Signin },
  { 
    path: "/dashboard", 
    component: Dashboard, 
    meta: { requiresAuth: true } 
  },
  { 
    path: "/admin", 
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true }
   },

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 🚀 Role-Based Navigation Guard
router.beforeEach(async(to, from, next) => {
  const authStore = useAuthStore();
  let user = auth.currentUser;
  
  if (authStore.isLoading) {
    next(); // Allow loading
    return;
  }

  if (!user) {
    await new Promise((resolve) => {
      onAuthStateChanged(auth, (firebaseUser) => {
        user = firebaseUser;
        resolve();
      });
    });
  }


  if (to.meta.requiresAuth) {
    if (!user) {
      next("/signin"); // ✅ Redirect unauthenticated users
    } else {
      // Fetch user role from Firestore
      await authStore.fetchUser();  // ✅ Ensure role is set in Pinia store

      if (to.meta.requiresAdmin && authStore.role !== "admin") {
        next("/dashboard"); // ✅ Redirect non-admins to dashboard
      } else {
        next();
      }
    }
  } else {
    next(); // ✅ Allow access to public routes
  }
});

export default router;