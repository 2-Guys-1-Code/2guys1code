<template>
    <v-btn @click="switchLocale">
        Switch Locale
    </v-btn>
</template>

<script setup lang="ts">
import { useLocale } from 'vuetify'
const { current } = useLocale()
const switchLocale = () => {
    if (current.value === 'en') {
        current.value = 'fr'
    } else {
        current.value = 'en'
    }
}
</script>
  