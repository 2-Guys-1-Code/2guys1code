<template>
  <div data-test="seat">seat {{ player ? player.name : 'empty' }}</div>
</template>

<style scoped></style>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  player: {
    type: Object,
    required: false,
  }
})

const status = computed(() => {
  return props.player ? 'ready' : 'empty'
})
</script>
