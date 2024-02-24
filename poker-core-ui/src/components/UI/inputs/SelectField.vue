<template>
    <!-- <v-select v-bind="$attrs"> -->
    <v-select v-bind="$attrs" :label="computedLabel" :class="{ required }" :required="required" :rules="computedRules">
        <template #message="{ message }: { message: string }">
            {{ reapplyPlaceholders(message) }}
        </template>
    </v-select>
</template>
  
<script setup lang="ts">
import { computed, inject } from 'vue'
import { reapplyPlaceholders } from '@/helpers/helpers'
import { validateRequired } from '@/helpers/validation'
// import { ValidationRule } from 'vuetify'

export interface Props {
    value?: Object
    label?: string
    required?: boolean
    rules?: any[] // Using any is uncool, but I can't find the correct type to import
}
const props = withDefaults(defineProps<Props>(), {
    value: null,
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
// function select(item) {
//     console.log(this.$refs.nativeSelect)
//     console.log('custom select', item)
//     this.$refs.nativeSelect.select(item)
// }

// defineExpose({
//     select,
// })
</script>
