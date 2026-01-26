<script setup>
import {ref, onMounted, computed} from 'vue'
import {fetchCaptcha} from '../api/captcha'
import {createComment} from "../api/comments.js";

const props = defineProps({
  parentId: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['created'])

const loading = ref(false)

const captcha = ref({
  id: null,
  image: null,
  value: '',
})

const form = ref({
  user_name: '',
  email: '',
  body: '',
})

async function loadCaptcha() {
  const { data } = await fetchCaptcha()
  captcha.value.id = data.captcha_id
  captcha.value.image = data.image
  captcha.value.value = ''
}

async function submit() {
  try {
    loading.value = true

    const payload = {
      ...form.value,
      parent: props.parentId,
      captcha_id: captcha.value.id,
      captcha_value: captcha.value.value,
    }

    await createComment(payload)

    emit('created')

    form.value = {
      user_name: '',
      email: '',
      body: '',
    }
    await loadCaptcha()
  } catch (e) {
    console.error(e)
    await loadCaptcha()
  } finally {
    loading.value = false
  }
}

const captchaSrc = computed(() =>
  captcha.value.image
    ? `data:image/png;base64,${captcha.value.image}`
    : null
)

onMounted(loadCaptcha)
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

        <div class="flex items-center gap-3">
          <img
            v-if="captchaSrc"
            :src="captchaSrc"
            alt="captcha"
             class="w-[160px] h-[60px] object-contain border rounded"
          />

          <input
            v-model="captcha.value"
            type="text"
            placeholder="Enter captcha"
            class="w-full rounded border border-gray-300 px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-gray-500"
            required
          />
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