<script setup>
const props = defineProps({
  file: {
    type: Object,
    required: true,
  }
})

const emit = defineEmits(['close'])
</script>

<template>
  <div
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="emit('close')"
  >
    <div class="bg-white max-w-[90vw] max-h-[90vh] p-4 rounded shadow">
      <!-- IMAGE -->
      <img
          v-if="file.type.startsWith('image/')"
          :src="file.preview"
          class="max-w-full max-h-[80vh]"
      />

      <!-- TEXT -->
      <pre
          v-else-if="file.type === 'text/plain'"
          class="max-h-[80vh] overflow-auto text-sm whitespace-pre-wrap"
      >
        {{ file.text }}
      </pre>

      <button
          class="mt-3 text-sm text-gray-500 hover:underline"
          @click="emit('close')"
      >
        Close
      </button>
    </div>
  </div>
</template>