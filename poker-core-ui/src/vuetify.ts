import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { createVueI18nAdapter } from 'vuetify/locale/adapters/vue-i18n'
import { createVuetify } from 'vuetify'
import i18n from './i18n'
import { useI18n } from 'vue-i18n'

const vuetify = createVuetify({
  components,
  directives,
  locale: {
    adapter: createVueI18nAdapter({ i18n, useI18n }),
  },
})

export default vuetify
