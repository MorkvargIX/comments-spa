<script setup>
import { ref, onMounted } from 'vue'
import CommentForm from '../components/CommentForm.vue'
import CommentList from '../components/CommentList.vue'
import CommentsFilter from '../components/CommentsFilter.vue'
import PaginationBar from '../components/PaginationBar.vue'
import { fetchComments } from '../api/comments.js'

const comments = ref([])
const showForm = ref(false)

const ordering = ref('-created_at')
const pagination = ref({
  page: 1,
  pageSize: 25,
  count: 0,
})

async function loadComments() {
  const { data } = await fetchComments({
    page: pagination.value.page,
    ordering: ordering.value,
  })

  comments.value = data.results
  pagination.value.count = data.count
}

function handleCreated() {
  showForm.value = false
  pagination.value.page = 1
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
        class="px-4 py-2 text-sm rounded bg-gray-500 transition duration-300 text-white hover:bg-gray-700 hover:cursor-pointer"
      >
        {{ showForm ? 'Hide form' : 'Add comment' }}
      </button>
    </div>

    <CommentsFilter
      :ordering="ordering"
      @change="(v) => { ordering = v; pagination.page = 1; loadComments() }"
    />

    <CommentForm v-if="showForm" @created="handleCreated" />

    <CommentList :comments="comments" />

    <PaginationBar
      :page="pagination.page"
      :page-size="pagination.pageSize"
      :total="pagination.count"
      @change="(p) => { pagination.page = p; loadComments() }"
    />
  </div>
</template>