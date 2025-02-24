<template>
   <div>
      <h1>Create an Account</h1>
      <p><input type="email" placeholder="Email" v-model="email"/></p>
      <p><input type="password" placeholder="Password" v-model="password"/></p>
      <p><button @click="register">Sign Up</button></p>
      <p><button @click="signInWithGoogle">Sign Up with Google</button></p>
      <p>Already have an account? <router-link to="/signin">Sign In</router-link></p>
   </div>
</template>

<script setup>
import {ref} from "vue"
import { getAuth, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

const auth = getAuth()
const email = ref("")
const password = ref("")

const register = () => {
   createUserWithEmailAndPassword(auth, email.value, password.value)
        .then((userCredential) => {
         console.log("Successfully registered:", userCredential.user)
        })
        .catch((error) => {
         console.log("Error registering:", error.message);
        })

}

const signInWithGoogle = () => {
  const provider = new GoogleAuthProvider();
  signInWithPopup(auth, provider)
    .then((result) => {
      console.log("Google sign-in success:", result.user);
    })
    .catch((error) => {
      console.error("Google sign-in error:", error.message);
   });
};

</script>