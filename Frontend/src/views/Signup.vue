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
import { useRouter } from "vue-router";
import { getAuth, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

const auth = getAuth()
const email = ref("")
const password = ref("")
const router = useRouter()

const register = async () => {
   try {
    const userCredential = await createUserWithEmailAndPassword(auth, email.value, password.value);
    const user = userCredential.user;

    // 🔥 Store user role in Firestore (DEFAULT role: "user")
    await setDoc(doc(db, "users", user.uid), {
      role: "user", // Change to "admin" manually in Firestore for admin users
      email: user.email,
    });

    router.push("/dashboard"); // Redirect to dashboard after signup
  } catch (error) {
    console.error("Signup failed:", error.message);
  }
}

const signInWithGoogle = () => {
  const provider = new GoogleAuthProvider();
  signInWithPopup(auth, provider)
    .then((result) => {
      console.log("Google sign-in success:", result.user);
      router.push("/dashboard");
    })
    .catch((error) => {
      console.error("Google sign-in error:", error.message);
   });
};

</script>