<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <nav class="bg-white shadow-md px-6 py-4">
      <div class="max-w-6xl mx-auto flex justify-between items-center">
        <!-- Logo/Brand -->
        <div class="font-bold text-xl text-blue-600">
          <router-link to="/" class="flex items-center">
            <span class="ml-2">BalanceGame</span>
          </router-link>
        </div>
        
        <!-- Navigation Links -->
        <div class="flex space-x-6">
          <router-link 
            to="/signup" 
            class="px-4 py-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-colors duration-200"
            active-class="bg-blue-50 text-blue-600 font-medium"
          >
            Sign Up
          </router-link>
          
          <router-link 
            to="/signin" 
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors duration-200"
            active-class="bg-blue-700"
          >
            Sign In
          </router-link>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="flex-grow">
      <router-view></router-view>
    </main>
  </div>
</template>

<style>
/* You can add any global styles here if needed */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body {
  font-family: 'Inter', sans-serif;
}
</style>