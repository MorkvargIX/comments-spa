<script setup>
import CommentItem from './CommentItem.vue'

const props = defineProps({
  comments: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <div class="space-y-4 rounded-lg border border-gray-100 bg-white shadow-sm mb-5">
    <CommentItem
      v-for="comment in comments"
      :key="comment.id"
      :comment="comment"
    />
  </div>
</template>