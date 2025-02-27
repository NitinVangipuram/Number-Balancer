<template>
    <div>
      <h1>Sign In</h1>
      <p><input type="email" placeholder="Email" v-model="email" /></p>
      <p><input type="password" placeholder="Password" v-model="password" /></p>
      <p><button @click="signIn">Sign In</button></p>
      <p><button @click="signInWithGoogle">Sign In with Google</button></p>
      <p>Don't have an account? <router-link to="/signup">Sign Up</router-link></p>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import { useRouter } from "vue-router";
  import { getAuth, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup} from "firebase/auth";

  const auth = getAuth();
  const email = ref("");
  const password = ref("");
  const router = useRouter()
  
  const signIn = () => {
    signInWithEmailAndPassword(auth, email.value, password.value)
      .then((userCredential) => {
        console.log("Successfully signed in:", userCredential.user);
        router.push("/dashboard")
      })
      .catch((error) => {
        console.error("Error signing in:", error.message);
      });
  };
  
  const signInWithGoogle = () => {
    const provider = new GoogleAuthProvider();
    signInWithPopup(auth, provider)
      .then((result) => {
        console.log("Google sign-in success:", result.user);
        router.push("/dashboard")
      })
      .catch((error) => {
        console.error("Google sign-in error:", error.message);
      });
  };
  
  </script>
  