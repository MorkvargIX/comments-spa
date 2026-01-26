<script setup>
import { ref, onMounted } from 'vue'
import CommentForm from '../components/CommentForm.vue'
import CommentList from '../components/CommentList.vue'
import { fetchComments } from '../api/comments.js'

const comments = ref([])
const showForm = ref(false)

async function loadComments() {
  const { data } = await fetchComments()
  comments.value = data.results
}

function handleCreated() {
  showForm.value = false
  loadComments()
}

onMounted(loadComments)
</script>

<template>
  <div class="max-w-3xl mx-auto py-8 space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-xl font-bold">Comments SPA</h1>

      <button
        @click="showForm = !showForm"
        class="px-4 py-2 text-sm rounded bg-gray-500 text-white hover:bg-gray-700"
      >
        {{ showForm ? 'Hide form' : 'Add comment' }}
      </button>
    </div>

    <CommentForm
      v-if="showForm"
      @created="handleCreated"
    />

    <CommentList :comments="comments" />
  </div>
</template>