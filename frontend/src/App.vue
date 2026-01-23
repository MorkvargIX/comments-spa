<script setup>
import CommentList from './components/CommentList.vue'
import CommentForm from './components/CommentForm.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-3xl mx-auto py-8 px-4">
      <h1 class="text-2xl font-bold mb-6">
        Comments
      </h1>

      <CommentForm />

      <div class="mt-8">
        <CommentList />
      </div>
    </div>
  </div>
</template>
