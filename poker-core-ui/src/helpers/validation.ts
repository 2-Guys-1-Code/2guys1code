// import i18n from '@/i18n'

// const $t = i18n.global.t as (a: string, b?: {}) => string

function validateBetween(min: number, max: number) {
  return (value: string) => {
    if (!value && value !== '0') return true
    const intVal = Number(value)
    if (intVal > max) return `$vuetify.validation.maxNumber{max:${max}}`
    if (intVal < min) return `$vuetify.validation.minNumber{min:${min}}`
    return true
  }
}

function validateRequired(value: string) {
  if (!value) {
    return '$vuetify.validation.required'
  }
  return true
}

function validateMinStringLength(length: number) {
  return (value: string) => {
    if (!value) {
      return true
    }

    if (value.length < length) {
      return `$vuetify.validation.minStringLength{length:${length}}`
    }

    return true
  }
}

function validateStringContainsNumber(value: string) {
  if (!value) {
    return true
  }
  // regex to match a string containing a number anywhere
  const regex = /\d/
  if (!regex.test(value)) {
    return '$vuetify.validation.stringContainsNumber'
  }

  return true
}

function validateStringContainsLowercase(value: string) {
  if (!value) {
    return true
  }
  //regex to match a string containing a capital letter anywhere
  const regex = /[a-z]/
  if (!regex.test(value)) {
    return '$vuetify.validation.stringContainsLowercase'
  }

  return true
}

function validateStringContainsUppercase(value: string) {
  if (!value) {
    return true
  }
  //regex to match a string containing a capital letter anywhere
  const regex = /[A-Z]/
  if (!regex.test(value)) {
    return '$vuetify.validation.stringContainsUppercase'
  }

  return true
}

function validateStringContainsSpecialCharacter(value: string) {
  if (!value) {
    return true
  }
  //regex to match a string containing a special character anywhere
  const regex = /[!@#$%^&*(),.?":{}|<>]/
  if (!regex.test(value)) {
    return '$vuetify.validation.stringContainsSpecialCharacter'
  }

  return true
}

function validatePassword(value: string) {
  if (!value) {
    return true
  }

  let results = [
    validateMinStringLength(8),
    validateStringContainsNumber,
    validateStringContainsLowercase,
    validateStringContainsUppercase,
    validateStringContainsSpecialCharacter,
  ].map((validator) => {
    const result = validator(value)
    if (result !== true) {
      return result
    }
  }).filter((r) => r)

  if (results.length > 0) {
    return results[0]
  }

  return true
}

function validateSame(value: string, otherValue: string, message: string) {
  if (!value) {
    return true
  }

  if (value !== otherValue) {
    return message
  }

  return true
}

function validateSameAs(otherValue: string, otherLabel: string) {
  if (otherLabel === null) throw new Error('otherLabel is required for the validation message.')
  

  return (value: string) => {
    return validateSame(value, otherValue, `$vuetify.validation.sameAs{other:${otherLabel}}`)
  }
}

function validatePasswordsMatch(otherValue: string) {
  return (value: string) => {
    return validateSame(value, otherValue, '$vuetify.validation.passwordsDoNotMatch')
  }
}

export { validateBetween, validateRequired, validateMinStringLength, validateStringContainsLowercase, validateStringContainsUppercase, validateStringContainsNumber, validateStringContainsSpecialCharacter, validatePassword, validateSameAs, validatePasswordsMatch }
