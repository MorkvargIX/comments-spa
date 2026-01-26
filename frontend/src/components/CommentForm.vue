<script setup>
import {ref, onMounted, nextTick, computed} from 'vue'
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
const bodyRef = ref(null)
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

function wrapSelection(openTag, closeTag) {
  const textarea = bodyRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd

  const before = form.value.body.slice(0, start)
  const selected = form.value.body.slice(start, end)
  const after = form.value.body.slice(end)

  form.value.body =
    before + openTag + selected + closeTag + after

  nextTick(() => {
    textarea.focus()
    textarea.selectionStart = start + openTag.length
    textarea.selectionEnd = end + openTag.length
  })
}

function insertLink() {
  const url = prompt('Enter URL')
  if (!url) return

  wrapSelection(
    `<a href="${url}" title="">`,
    `</a>`
  )
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

        <div class="flex gap-2 text-sm">
          <button
            type="button"
            class="px-2  border rounded hover:bg-gray-100 hover:cursor-pointer"
            @click="wrapSelection('<i>', '</i>')"
          >
            I
          </button>

          <button
            type="button"
            class="px-2 border rounded hover:bg-gray-100 font-bold hover:cursor-pointer"
            @click="wrapSelection('<strong>', '</strong>')"
          >
            B
          </button>

          <button
            type="button"
            class="px-2 border rounded hover:bg-gray-100 font-mono hover:cursor-pointer"
            @click="wrapSelection('<code>', '</code>')"
          >
            C
          </button>

          <button
            type="button"
            class="px-2 border rounded hover:bg-gray-100 hover:cursor-pointer"
            @click="insertLink"
          >
            Link
          </button>
        </div>

        <textarea
          ref="bodyRef"
          v-model="form.body"
          placeholder="Comment..."
          rows="4"
          class="w-full rounded border border-gray-300 px-3 py-2 text-sm
                 focus:outline-none focus:ring-2 focus:ring-gray-500 resize-none"
          required
        />

        <div
          v-if="form.body"
          class="border rounded p-2 bg-gray-50 text-sm whitespace-pre-wrap"
        >
          <p class="font-semibold mb-1">Preview:</p>
          <div v-html="form.body"></div>
        </div>

        <div class="flex items-center gap-3">
          <img
            v-if="captchaSrc"
            :src="captchaSrc"
            alt="captcha"
             class="w-40 h-15 object-contain border rounded"
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