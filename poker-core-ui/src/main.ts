import './assets/main.css'
import 'vuetify/styles'

import App from './App.vue'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import i18n from './i18n'
import router from './router'
import vuetify from './vuetify'

const app = createApp(App)

app.use(i18n)
app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')

// app.config.globalProperties.$t = i18n.global.t
