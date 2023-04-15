import i18n from '@/i18n'

const $t = i18n.global.t as (a: string, b?: {}) => string

function makeid(length: number) {
  let result = ''
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  const charactersLength = characters.length
  let counter = 0
  while (counter < length) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength))
    counter += 1
  }
  return result
}

function reapplyPlaceholders(value: string) {
  const key = value.replace(/\{.*\}/, '')
  const matches = [...value.matchAll(/\{([^:]*):([^:]*)\}/g)].reduce(
    (acc: Record<string, string>, m) => {
      const [key, value] = m.slice(-2)
      acc[key] = value
      return acc
    },
    {},
  )
  return $t(key, matches)
}

export { makeid, reapplyPlaceholders }
