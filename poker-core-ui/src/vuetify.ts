import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { createVueI18nAdapter } from 'vuetify/locale/adapters/vue-i18n'
import { createVuetify } from 'vuetify'
import i18n from './i18n'
import { useI18n } from 'vue-i18n'

import { fa } from "vuetify/iconsets/fa";
import { aliases, mdi } from "vuetify/iconsets/mdi";

const vuetify = createVuetify({
  components,
  directives,
  locale: {
    adapter: createVueI18nAdapter({ i18n, useI18n }),
  },
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: {
      mdi,
      fa,
    },
  },
})

export default vuetify
