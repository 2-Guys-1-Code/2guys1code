import './assets/main.css'
import 'vuetify/styles'

import App from './App.vue'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import i18n from './i18n'
import { createRouter } from './router'
import { useUserstore } from '@/stores/user'
import vuetify from './vuetify'
import { useNotify } from './plugins/notify'
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import "@mdi/font/css/materialdesignicons.css";
import "@fortawesome/fontawesome-free/css/all.css";

const app = createApp(App)

app.use(i18n)
app.use(createPinia())

const router = createRouter({}, useUserstore())
app.use(router)

app.use(vuetify)
app.use(useNotify())

async function prepareApp() {
  if (
    process.env.NODE_ENV === 'development' ||
    process.env.NODE_ENV === 'test'
  ) {
    const { worker } = await import('./tests/mocks/node')
    return worker.start()
  }

  return Promise.resolve()
}

prepareApp().then(() => {
  app.mount('#app')
})
