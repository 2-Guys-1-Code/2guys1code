import { createApp } from 'vue'
// import Vue from 'vue'
import { createPinia } from 'pinia'
import { createVueI18nAdapter } from 'vuetify/locale/adapters/vue-i18n'
import { createI18n, useI18n, type I18n } from 'vue-i18n'
// import VueI18n from 'vue-i18n'
import App from './App.vue'
import router from './router'

// Vuetify
import 'vuetify/styles'
import { createVuetify, useLocale } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import './assets/main.css'
import i18n from './i18n'
import vuetify from './vuetify'

// const i18n: I18n = new (createI18n as any)({
//     legacy: false, // Vuetify does not support the legacy mode of vue-i18n
//     locale: 'en',
//     fallbackLocale: 'fr',
//     messages,
// })
// const i18n = new (VueI18n as any)({
//     locale: 'ja',
//     messages: {
//         en: {
//             message: {
//                 hello: 'hello world',
//                 greeting: 'good morning'
//             }
//         },
//         ja: {
//             message: {
//                 hello: 'こんにちは、世界',
//                 greeting: 'おはようございます'
//             }
//         }
//     }
// })

// const vuetify = createVuetify({
//     components,
//     directives,
//     locale: {
//         adapter: createVueI18nAdapter({ i18n, useI18n })
//     }
// })
const app = createApp(App)

app.use(i18n)
app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')

// app.config.globalProperties.$t = i18n.global.t
