import { createRouter, createWebHistory } from "vue-router";
import Signup from "../views/Signup.vue";
import Signin from "../views/Signin.vue";
import Dashboard from "../views/Dashboard.vue";
import { getAuth, onAuthStateChanged } from "firebase/auth";

const auth = getAuth();

const routes = [
  { path: "/signup", component: Signup },
  { path: "/signin", component: Signin },
  { 
    path: "/dashboard", 
    component: Dashboard, 
    meta: { requiresAuth: true } 
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation Guard
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    onAuthStateChanged(auth, (user) => {
      if (!user) {
        next("/signin");
      } else {
        next();
      }
    });
  } else {
    next();
  }
});

export default router;
