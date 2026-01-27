<script setup>
import { ref } from 'vue'
import LightBox from './LightBox.vue'
import {fetchAttachmentText} from "../api/attachments.js";

const props = defineProps({
  attachments: {
    type: Array,
    default: () => []
  }
})

const lightBox = ref({
  open: false,
  file: null
})

async function openAttachment(att) {
  if (att.type === 'IMAGE' || att.type === 'image') {
    lightBox.value = {
      open: true,
      file: {
        type: 'image',
        src: att.url,
        name: att.original_name
      }
    }
    return
  }

  if (att.type === 'TEXT' || att.type === 'text') {
    const text = await fetchAttachmentText(att.url)

    lightBox.value = {
      open: true,
      file: {
        type: 'text',
        text,
        name: att.original_name
      }
    }
  }
}
</script>

<template>
  <div v-if="attachments.length" class="mt-3 flex flex-wrap gap-2">
    <div
      v-for="file in attachments"
      :key="file.id"
      class="flex items-center gap-2 text-sm"
    >
      <!-- IMAGE -->
      <template v-if="file.type === 'IMAGE' || file.type === 'image'">
        <img
          :src="file.url"
          class="block w-20 h-16 object-cover rounded cursor-pointer border"
          @click="openAttachment(file)"
        />
      </template>

      <!-- TEXT -->
      <template v-else>
        <button
          class="text-gray-600 hover:underline text-sm hover:cursor-pointer"
          @click="openAttachment(file)"
        >
          📄 {{ file.original_name }}
        </button>
      </template>
    </div>
  </div>

  <LightBox
    v-if="lightBox.open"
    :file="lightBox.file"
    @close="lightBox.open = false"
  />
</template>