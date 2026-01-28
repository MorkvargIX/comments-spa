<script setup>
import {ref, onMounted, nextTick, computed} from 'vue'
import {fetchCaptcha} from '../api/captcha'
import {createComment} from "../api/comments.js";
import LightBox from "./LightBox.vue";

const props = defineProps({
  parentId: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['created'])

const lightBox = ref({
  open: false,
  file: null
})

const loading = ref(false)
const bodyRef = ref(null)
const captcha = ref({
  id: null,
  image: null,
  value: '',
})
const files = ref([])
const fileInput = ref(null)

const form = ref({
  user_name: '',
  email: '',
  body: '',
})

const errors = ref({
  user_name: null,
  email: null,
  body: null,
  captcha: null,
  file: null,
  home_page: null,
  non_field_errors: null,
})

function handleFiles(event) {
  const selected = Array.from(event.target.files)

  selected.forEach(file => {
    const exists = files.value.find(
      f => f.name === file.name && f.size === file.size
    )
    if (exists) return

    const item = {
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      preview: URL.createObjectURL(file),
    }

    if (file.type === 'text/plain') {
      const reader = new FileReader()
      reader.onload = e => {
        item.text = e.target.result
      }
      reader.readAsText(file)
    }

    files.value.push(item)
  })

  event.target.value = ''
}

function openPreview(file) {
  if (file.type.startsWith('image/')) {
    lightBox.value = {
      open: true,
      file: {
        type: 'image',
        src: file.preview,
        name: file.name,
      }
    }
    return
  }

  if (file.type === 'text/plain') {
    lightBox.value = {
      open: true,
      file: {
        type: 'text',
        text: file.text,
        name: file.name,
      }
    }
  }
}

function removeFile(index) {
  files.value.splice(index, 1)
}

async function loadCaptcha() {
  const {data} = await fetchCaptcha()
  captcha.value.id = data.captcha_id
  captcha.value.image = data.image
  captcha.value.value = ''
}

function resetForm() {
  form.value = {
    user_name: '',
    email: '',
    body: '',
  }

  files.value = []

  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function submit() {
  try {
    Object.keys(errors.value).forEach(k => errors.value[k] = null)

    let hasError = false

    if (!form.value.user_name.trim()) {
      errors.value.user_name = 'User name is required'
      hasError = true
    }

    if (!form.value.email.includes('@')) {
      errors.value.email = 'Invalid email'
      hasError = true
    }

    if (!form.value.body.trim()) {
      errors.value.body = 'Comment cannot be empty'
      hasError = true
    }

    if (!captcha.value.value) {
      errors.value.captcha = 'Captcha is required'
      hasError = true
    }

    if (hasError) return

    loading.value = true

    const formData = new FormData()

    formData.append('user_name', form.value.user_name)
    formData.append('email', form.value.email)
    formData.append('body', form.value.body)

    if (props.parentId) {
      formData.append('parent', props.parentId)
    }

    formData.append('captcha_id', captcha.value.id)
    formData.append('captcha_value', captcha.value.value)

    files.value.forEach(item => {
      formData.append('files', item.file)
    })

    await createComment(formData)

    emit('created')

    resetForm()
    await loadCaptcha()
  } catch (e) {
    if (e.response?.data) {
      const data = e.response.data

      Object.keys(data).forEach(key => {
        const message = Array.isArray(data[key]) ? data[key][0] : data[key]

        if (key === 'captcha_value' || key === 'captcha_id' || key === 'non_field_errors') {
          errors.value.captcha = message
          return
        }
        if (key in errors.value) {
          errors.value[key] = message
          return
        }

      })
    }
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

function inputClass(error) {
  return [
    'w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2',
    error
        ? 'border-red-500 focus:ring-red-500'
        : 'border-gray-300 focus:ring-gray-500'
  ]
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

    <form @submit.prevent="submit" novalidate>
      <div class="grid grid-cols-1 gap-3">
        <input
            v-model="form.user_name"
            @focus="errors.user_name = null"
            type="text"
            placeholder="User name"
            :class="inputClass(errors.user_name)"
        />
        <p v-if="errors.user_name" class="text-xs text-red-500">
          {{ errors.user_name }}
        </p>
        <input
          v-model="form.home_page"
          @focus="errors.home_page = null"
          type="url"
          placeholder="Home page (optional)"
          :class="inputClass(errors.home_page)"
        />
        <p v-if="errors.home_page" class="text-xs text-red-500">
          {{ errors.home_page }}
        </p>

        <input
            v-model="form.email"
            @focus="errors.email = null"
            type="email"
            placeholder="Email"
            :class="inputClass(errors.email)"
        />
        <p v-if="errors.email" class="text-xs text-red-500">
          {{ errors.email }}
        </p>

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
            @focus="errors.body = null"
            placeholder="Comment..."
            rows="4"
            :class="inputClass(errors.body)"
        />
        <p v-if="errors.body" class="text-xs text-red-500">
          {{ errors.body }}
        </p>

        <div
            v-if="form.body"
            class="border rounded p-2 bg-gray-50 text-sm whitespace-pre-wrap"
        >
          <p class="font-semibold mb-1">Preview:</p>
          <div v-html="form.body"></div>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-m font-medium text-gray-700">
            Attach files
          </label>

          <input
              ref="fileInput"
              type="file"
              id="files"
              class="hidden"
              multiple
              @change="handleFiles"
              :class="inputClass(errors.file)"
          />
          <p v-if="errors.file" class="text-xs text-red-500">
            {{ errors.file }}
          </p>

          <label
              for="files"
              class="px-3 py-2 border rounded cursor-pointer hover:bg-gray-100 text-sm"
          >
            Browse files
          </label>

          <div
              v-if="files.length"
              class="border rounded p-2 bg-gray-50 space-y-1"
          >
            <div
                v-for="(file, index) in files"
                :key="file.name + index"
                class="flex justify-between items-center text-sm cursor-pointer hover:bg-gray-100 px-1 rounded"
                @click="openPreview(file)"
            >
            <span class="truncate">
              {{ file.name }} ({{ Math.round(file.size / 1024) }} KB)
            </span>

              <button
                  type="button"
                  class="text-red-500 hover:underline hover:cursor-pointer"
                  @click="removeFile(index)"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <img
              v-if="captchaSrc"
              :src="captchaSrc"
              alt="captcha"
              class="w-40 h-15 object-contain border rounded"
          />

          <div class="flex flex-col">
            <input
                v-model="captcha.value"
                @focus="errors.captcha = null"
                type="text"
                placeholder="Enter captcha"
                :class="inputClass(errors.captcha)"
            />
            <p v-if="errors.captcha" class="text-xs text-red-500">
              {{ errors.captcha }}
            </p>
          </div>
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
  <LightBox
    v-if="lightBox.open"
    :file="lightBox.file"
    @close="lightBox.open = false"
  />
</template>