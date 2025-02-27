import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { createPinia } from "pinia";
import firebase from './firebase';


const pinia = createPinia();  // ✅ Create Pinia instance
const auth = getAuth(firebase)

const app = createApp(App)

onAuthStateChanged(auth, (user) => {
    if (!user) {
      router.push("/signin"); // Redirect logged-in users to dashboard
    }
  });  

app.use(pinia)
app.use(router)
app.mount('#app')


