<script setup>
import {computed} from "vue";
const props = defineProps({
  page: Number,
  pageSize: Number,
  total: Number,
})

const emit = defineEmits(['change'])

const totalPages = computed(() =>
  Math.ceil(props.total / props.pageSize)
)
function selectPage(value) {
  let defaultStyles = 'transition duration-200 hover:cursor-pointer hover:scale-120'
  return value === props.page ? `font-bold underline ${defaultStyles}` : defaultStyles
}
</script>

<template>
  <div class="flex gap-2 justify-center mt-6">
    <button
      v-for="p in totalPages"
      :key="p"
      @click="p !== page && emit('change', p)"
      :class="selectPage(p)"
    >
      {{ p }}
    </button>
  </div>
</template>