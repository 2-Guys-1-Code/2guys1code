<template>
  <v-btn @click="switchLocale">Switch Locale</v-btn>
</template>

<script setup lang="ts">
// console.log('LocaleSwitcher.vue')
// // debugger;
import { useLocale } from 'vuetify'
const { current } = useLocale()
const switchLocale = () => {
  if (current.value === 'en') {
    current.value = 'fr'
  } else {
    current.value = 'en'
  }
}

// import { getCurrentLocale, switchLocale } from '@/i18n/helpers'

// const toggleLocale = () => {
//   const current = getCurrentLocale()
//   if (current === 'en') {
//     switchLocale('fr')
//   } else {
//     switchLocale('en')
//   }
// }
</script>
