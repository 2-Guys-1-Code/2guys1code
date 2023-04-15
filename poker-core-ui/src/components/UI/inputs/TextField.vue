<template>
  <v-text-field
    :label="computedLabel"
    :class="{ required }"
    :required="required"
    :rules="computedRules"
  >
    <template #message="{ message }: { message: string }">
      {{ reapplyPlaceholders(message) }}
    </template>
  </v-text-field>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'
import { reapplyPlaceholders } from '@/helpers/helpers'
import { validateRequired } from '@/helpers/validation'
// import { ValidationRule } from 'vuetify'

export interface Props {
  label?: string
  required?: boolean
  rules?: any[] // Using any is uncool, but I can't find the correct type to import
}
const props = withDefaults(defineProps<Props>(), {
  label: 'hello',
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

<!-- <script lang="ts">
export default {
  name: 'TextField',
  // extends: VTextField,

  props: {
    label: {
      type: String,
    },
    required: {
      type: Boolean,
      default: false,
    },
    rules: {
      type: Array,
      default: () => {
        return []
      },
    },
  },

  computed: {
    computedLabel: function () {
      return this.required ? `${this.label} *` : this.label
    },
    computedRules: function () {
      return this.required ? [this.validateRequired, ...this.rules] : this.rules
    },
  },
  methods: {
    validateRequired(value: string) {
      if (!value) return this.$t('$vuetify.validation.required')
      return true
    },
  },
} as Vue.ComponentOptions<Vue>
</script> -->
