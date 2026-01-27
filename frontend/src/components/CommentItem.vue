<script setup>
import {ref, computed} from 'vue'
import avatar from '../assets/vue.svg'
import CommentForm from './CommentForm.vue'
import {fetchReplies} from "../api/comments.js";

const props = defineProps({
  comment: {
    type: Object,
    required: true,
  },
  level: {
    type: Number,
    default: 0
  },
  parent: {
    type: Object,
    default: null
  }
})

const MAX_LENGTH = 200
const MAX_BORDER_LEVEL = 6
const MAX_INDENT_LEVEL = 6

const showReplyForm = ref(false)
const expanded = ref(false)

const replies = ref([])
const repliesLoaded = ref(false)
const repliesVisible = ref(false)
const loadingReplies = ref(false)

const isLong = computed(() => props.comment.body.length > MAX_LENGTH)
const displayedText = computed(() => {
  if (expanded.value || !isLong.value) {
    return props.comment.body
  }
  return props.comment.body.slice(0, MAX_LENGTH) + '…'
})

const repliesWrapperClass = computed(() => {
  return [
    'mt-3 space-y-3',
    props.level <= MAX_BORDER_LEVEL
      ? 'border-l-2 border-dashed border-gray-300'
      : '',
    props.level <= MAX_INDENT_LEVEL
      ? 'pl-2'
      : ''
  ]
})


function formatDate(value) {
  if (!value) return ''

  const date = new Date(value)

  const dd = String(date.getDate()).padStart(2, '0')
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const yy = String(date.getFullYear()).slice(-2)

  const hh = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')

  return `${dd}.${mm}.${yy} in ${hh}:${min}`
}

function toTitleCase(str = '') {
  return str
      .toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
}


function toggleReply() {
  showReplyForm.value = !showReplyForm.value
}

async function handleReplyCreated() {
  showReplyForm.value = false

  loadingReplies.value = true
  const {data} = await fetchReplies(props.comment.id)
  replies.value = data.results
  repliesLoaded.value = true
  repliesVisible.value = true
  loadingReplies.value = false
}

async function toggleReplies() {
  if (!repliesLoaded.value) {
    loadingReplies.value = true
    const {data} = await fetchReplies(props.comment.id)
    replies.value = data.results
    repliesLoaded.value = true
    loadingReplies.value = false
  }

  repliesVisible.value = !repliesVisible.value
}

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
        {{ formatDate(comment.created_at) }}
      </span>
      <span
          v-if="props.parent"
          class="rounded space-y-3 text-xs text-gray-400"
      >
        Replies to <span class="font-semibold text-gray-600">
          {{ props.parent.user_name }}
        </span>
      </span>
    </div>

    <!-- Body -->
    <div
        class="overflow-hidden transition-all duration-300 ease-in-out"
        :class="expanded ? 'max-h-[9999px]' : 'max-h-24'"
    >
      <div
          class="prose prose-sm max-w-none whitespace-pre-wrap"
          v-html="displayedText"
      />
    </div>

    <!-- Actions -->
    <div class="flex justify-between mt-2 text-xs text-gray-500">
      <div class="flex gap-3">
        <span
            class="cursor-pointer hover:text-gray-800 hover:underline"
            @click="toggleReply"
        >
          Reply
        </span>

        <span
            v-if="comment.replies_count > 0"
            class="cursor-pointer hover:text-gray-800 hover:underline"
            @click="toggleReplies"
        >
          {{ comment.replies_count }} replies
        </span>
      </div>

      <span
          v-if="isLong"
          @click="expanded = !expanded"
          class="cursor-pointer hover:text-gray-800 hover:underline select-none"
      >
        {{ expanded ? 'Collapse' : 'Expand' }}
      </span>
    </div>
    <div
        v-if="repliesVisible && replies.length && level <= 2"
        class="mt-3 border-l rounded space-y-3 pl-2"
    >
      <CommentItem
          v-for="reply in replies"
          :key="reply.id"
          :comment="reply"
          :level="level + 1"
          :parent="props.comment"
      />
    </div>
  </div>

  <div
      v-if="repliesVisible && replies.length && level > 2"
      :class="repliesWrapperClass"
  >
    <CommentItem
        v-for="reply in replies"
        :key="reply.id"
        :comment="reply"
        :level="level + 1"
        :parent="props.comment"
    />
  </div>
  <CommentForm
      v-if="showReplyForm"
      :parent-id="comment.id"
      @created="handleReplyCreated"
  />
</template>
