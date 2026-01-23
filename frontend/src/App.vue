<script setup>
import CommentList from './components/CommentList.vue'
</script>

<template>
  <div class="min-h-screen">
    <header class="bg-white shadow p-4 mb-6">
      <h1 class="text-xl font-bold">
        Comments SPA
      </h1>
    </header>

    <main class="max-w-3xl mx-auto px-4">
      <CommentList />
    </main>
  </div>
</template>
