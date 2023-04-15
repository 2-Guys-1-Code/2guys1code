import i18n from '@/i18n'

const $t = i18n.global.t as (a: string, b?: {}) => string

function validateBetween(min: number, max: number) {
  return (value: string) => {
    if (!value) return true
    const intVal = Number(value)
    console.log(intVal)
    if (intVal > max) return `$vuetify.validation.maxNumber{limit:${max}}`
    if (intVal < min) return `$vuetify.validation.minNumber{limit:${min}}`
    return true
  }
}

function validateRequired(value: string) {
  if (!value) return '$vuetify.validation.required'
  return true
}

export { validateBetween, validateRequired }
