<script setup>
import { ref } from 'vue'

const emit = defineEmits(['change'])

const active = ref('-created_at')

function buttonClass(value) {
  return [
    'border rounded-md px-2 py-1 transition hover:cursor-pointer',
    active.value === value
      ? 'bg-gray-700 text-white'
      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
  ]
}

function select(value) {
  active.value = value
  emit('change', value)
}
</script>

<template>
  <div class="flex gap-2 text-sm">
    <button :class="buttonClass('-created_at')" @click="select('-created_at')">
      Newest
    </button>

    <button :class="buttonClass('created_at')" @click="select('created_at')">
      Oldest
    </button>

    <button :class="buttonClass('user_name')" @click="select('user_name')">
      User A–Z
    </button>

    <button :class="buttonClass('-user_name')" @click="select('-user_name')">
      User Z–A
    </button>

    <button :class="buttonClass('email')" @click="select('email')">
      Email
    </button>
  </div>
</template>