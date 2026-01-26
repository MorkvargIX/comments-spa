<script setup>
import {ref} from 'vue'

import {createComment} from "../api/comments.js";

const props = defineProps({
  parentId: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['created'])

const loading = ref(false)

const form = ref({
  user_name: '',
  email: '',
  body: '',
})

async function submit() {
  try {
    loading.value = true

    const payload = {
      ...form.value,
      parent: props.parentId,
    }

    await createComment(payload)

    emit('created')

    form.value = {
      user_name: '',
      email: '',
      body: '',
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>


<template>
  <div class="bg-white border border-gray-200 rounded-md p-4 ">
    <h3 class="text-sm font-semibold text-gray-800 mb-3">
      {{ parentId ? 'Reply' : 'New comment' }}
    </h3>

    <form @submit.prevent="submit">
      <div class="grid grid-cols-1 gap-3">
        <input
            v-model="form.user_name"
            type="text"
            placeholder="User name"
            class="w-full rounded border border-gray-300 px-3 py-2 text-sm
         focus:outline-none focus:ring-2 focus:ring-gray-500"
            required
        />

        <input
            v-model="form.email"
            type="email"
            placeholder="Email"
            class="w-full rounded border border-gray-300 px-3 py-2 text-sm
         focus:outline-none focus:ring-2 focus:ring-gray-500"
            required
        />

        <textarea
            v-model="form.body"
            placeholder="Comment..."
            rows="4"
            class="w-full rounded border border-gray-300 px-3 py-2 text-sm
         focus:outline-none focus:ring-2 focus:ring-gray-500 resize-none"
            required
        />

        <!-- CAPTCHA пока заглушка -->
        <div class="text-xs text-gray-400">
          CAPTCHA will be there
        </div>

        <div class="flex justify-end">
          <button
              type="submit"
              class="px-4 py-2 text-sm font-medium text-white bg-gray-600 rounded hover:bg-gray-700"
              :disabled="loading"
          >
            {{ loading ? 'Sending...' : 'Send' }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>