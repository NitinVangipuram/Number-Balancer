<template>
    <h1>Welcome to the Dashboard</h1>
    <button @click="logout">Logout</button>
  </template>
  
  <script setup>
  import { useRouter } from "vue-router";
  import { getAuth, signOut } from "firebase/auth";
  
  const router = useRouter();
  const auth = getAuth();
  
  const logout = () => {
    signOut(auth)
      .then(() => {
        router.push("/"); // Redirect to login after logout
      })
      .catch((error) => {
        console.error(error.message);
      });
  };
  </script>
  