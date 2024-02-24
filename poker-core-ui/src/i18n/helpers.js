import { useLocale } from 'vuetify'
import messages from './messages'

// This does not work outside of a component
const { current } = useLocale()

function getCurrentLocale() {
  return current.value
}

function switchLocale(locale) {
  if (!getLocales().includes(locale)) {
    throw new Error(`Locale ${locale} is not supported`)
  }
  current.value = locale
}

function getLocales() {
  return messages.keys().filter((key) => key !== 'test')
}

export { getCurrentLocale, getLocales, switchLocale }