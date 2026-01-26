<script setup>
import { ref, computed } from 'vue'
import avatar from '../assets/vue.svg'

const props = defineProps({
  comment: {
    type: Object,
    required: true,
  },
})

function toTitleCase(str = '') {
  return str
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const MAX_LENGTH = 200
const expanded = ref(false)

const isLong = computed(() => props.comment.body.length > MAX_LENGTH)

const displayedText = computed(() => {
  if (expanded.value || !isLong.value) {
    return props.comment.body
  }
  return props.comment.body.slice(0, MAX_LENGTH) + '…'
})
</script>


<template>
  <div class="bg-white rounded-md px-4 py-3">
    <!-- Header -->
    <div class="flex items-center gap-2 mb-2 ml-7">
      <img
        :src="avatar"
        alt="User avatar"
        class="w-8 h-8 rounded-full object-cover bg-gray-100"
      />
      <span class="text-sm font-bold text-gray-900">
        {{ toTitleCase(comment.user_name) }}
      </span>
      <span class="text-sm font-medium text-gray-400">
        {{ comment.created_at }}
      </span>
    </div>

    <!-- Body -->
    <div
      class="overflow-hidden transition-all duration-300 ease-in-out"
      :class="expanded ? 'max-h-[9999px]' : 'max-h-24'"
    >
      <div
        class="text-sm font-medium text-gray-700 leading-relaxed whitespace-pre-wrap"
        v-html="displayedText"
      />
    </div>

    <!-- Actions -->
    <div class="flex justify-between mt-2 text-xs text-gray-500">
      <span
        v-if="isLong"
        @click="expanded = !expanded"
        class="cursor-pointer hover:text-gray-800 hover:underline select-none"
      >
        {{ expanded ? 'Collapse' : 'Expand' }}
      </span>

      <span
        v-if="comment.replies_count > 0"
        class="cursor-pointer hover:text-gray-800 hover:underline"
      >
        {{ comment.replies_count }} replies
      </span>
    </div>
  </div>
</template>
