<template>
  <v-text-field :label="computedLabel" :class="{ required }" :required="required" :rules="computedRules">
    <template #message="{ message }: { message: string }">
      {{ reapplyPlaceholders(message) }}
    </template>
  </v-text-field>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'
import { reapplyPlaceholders } from '@/helpers/helpers'
import { validateRequired } from '@/helpers/validation'

export interface Props {
  label?: string
  required?: boolean
  rules?: any[]
}
const props = withDefaults(defineProps<Props>(), {
  label: '',
  required: false,
  rules: () => [],
})

const computedLabel = computed(() => {
  return props.required ? `${props.label} *` : props.label
})
const computedRules = computed(() => {
  return props.required ? [validateRequired, ...props.rules] : props.rules
})
</script>
