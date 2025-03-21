<template>
  <div class="signup-container">
    <div class="signup-card">
      <div class="logo-container">
        <img src="../beach-ball_375219.png" alt="Logo" class="logo" />
      </div>
      <h1 class="title">Create an Account</h1>
      <p class="subtitle">Join us today and start your journey</p>
      
      <div class="form-group">
        <label for="email">Email</label>
        <input 
          type="email" 
          id="email" 
          placeholder="Enter your email" 
          v-model="email"
          class="input-field"
        />
      </div>
      
      <div class="form-group">
        <label for="password">Password</label>
        <input 
          type="password" 
          id="password" 
          placeholder="Create a password" 
          v-model="password"
          class="input-field"
        />
      </div>
      
      <button @click="register" class="signup-button">
        Create Account
      </button>
      
      <div class="divider">
        <span>or</span>
      </div>
      
      <button @click="signInWithGoogle" class="google-button">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" class="google-icon" />
        Sign Up with Google
      </button>
      
      <p class="login-link">
        Already have an account? <router-link to="/signin">Sign In</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { getAuth, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import {doc, getFirestore, setDoc } from "firebase/firestore";
import firebase from "@/firebase";

const auth = getAuth();
const email = ref("");
const password = ref("");
const router = useRouter();
const db = getFirestore()

const register = async () => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email.value, password.value);
    const user = userCredential.user;

    await setDoc(doc(db, "users", user.uid), {
      role: "user", // Change to "admin" manually in Firestore for admin users
      email: user.email,
    });

    router.push("/dashboard"); // Redirect to dashboard after signup
  } catch (error: any) {
    console.error("Signup failed:", error.message);
  }
};

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

<style scoped>
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.signup-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  padding: 40px;
  text-align: center;
}

.logo-container {
  margin-bottom: 20px;
}

.logo {
  height: 60px;
  width: auto;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.input-field:focus {
  border-color: #646cff;
  outline: none;
}

.signup-button {
  width: 100%;
  padding: 14px;
  background-color: #646cff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.signup-button:hover {
  background-color: #535bf2;
}

.divider {
  display: flex;
  align-items: center;
  margin: 25px 0;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  border-bottom: 1px solid #ddd;
}

.divider span {
  padding: 0 10px;
  color: #777;
  font-size: 14px;
}

.google-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 12px;
  background-color: white;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.google-button:hover {
  background-color: #f5f5f5;
}

.google-icon {
  width: 20px;
  height: 20px;
  margin-right: 10px;
}

.login-link {
  margin-top: 30px;
  font-size: 14px;
  color: #666;
}

.login-link a {
  color: #646cff;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>






<!-- <template>
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

</script> -->