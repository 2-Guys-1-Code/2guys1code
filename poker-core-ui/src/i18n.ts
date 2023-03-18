// import { use } from 'vue';
// import VueI18n from 'vue-i18n';
import { createI18n, type I18n } from 'vue-i18n'
import messages from './i18n/messages'

// use(VueI18n);

const i18n: I18n = new (createI18n as any)({
  legacy: false, // Vuetify does not support the legacy mode of vue-i18n
  locale: 'en',
  fallbackLocale: 'fr',
  globalInjection: true,
  messages
})

export default i18n
