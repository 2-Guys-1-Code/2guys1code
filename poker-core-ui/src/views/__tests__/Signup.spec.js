import { describe, expect, it, vi, afterEach, beforeAll, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import Signup from '../Signup.vue'
import { createRouter } from '../../router'
import { useUserstore } from '@/stores/user'
import { flushPromises } from '@vue/test-utils'
import { Later } from '@/tests/helpers'

const fakeRepo = {
  signup: (data) => Promise.resolve(data),
}

const mountLocal = async (options = {}) => {
  const wrapper = mount(Signup, {
    props: {
      repoFactory: () => {
        return fakeRepo
      },
    },
    ...options
  })
  await wrapper.vm.$nextTick();
  return wrapper
}

const submitForm = async (wrapper) => {
    await wrapper.find('[data-test="button_submit"]').trigger('click')
    await flushPromises() // wait for validation
}

describe('Signup', () => {
  let router
  beforeAll(() => {
    setActivePinia(createPinia())
  })

  beforeEach(async () => {
    router = createRouter({}, useUserstore())
    useUserstore().$reset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('password field can be toggled to show the value', async () => {
    const wrapper = await mountLocal()
    
    const field = wrapper.find('[data-test="field_password"]')

    expect(field.find('input').element.type).toBe('password')
    await field.find('.v-icon--clickable').trigger('click')
    expect(field.find('input').element.type).toBe('text')

    await field.find('.v-icon--clickable').trigger('click')
    expect(field.find('input').element.type).toBe('password')
  })

  it('displays a password confirmation field', async () => {
    const wrapper = await mountLocal()
    const input = wrapper.find('[data-test="field_password-confirm"] input')
    expect(input.element.value).toBe('')
    expect(input.element.type).toBe('password')
  })

  it('password field can be toggled to show the value', async () => {
    const wrapper = await mountLocal()
    
    const confirmField = wrapper.find('[data-test="field_password-confirm"]')
    const passwordField = wrapper.find('[data-test="field_password"]')

    expect(confirmField.find('input').element.type).toBe('password')
    await confirmField.find('.v-icon--clickable').trigger('click')
    expect(confirmField.find('input').element.type).toBe('text')
    expect(passwordField.find('input').element.type).toBe('password') // Check that the other field is not affected

    await confirmField.find('.v-icon--clickable').trigger('click')
    expect(confirmField.find('input').element.type).toBe('password')
  })

  it('validates the form on submit', async () => {
    const wrapper = await mountLocal()

    await submitForm(wrapper)

    const usernameMessages = wrapper.findAll('[data-test="field_username"] .v-messages__message')
    expect(usernameMessages.length).toBe(1)
    expect(usernameMessages.at(0).text()).toBe('Required')

    const passwordMessages = wrapper.findAll('[data-test="field_password"] .v-messages__message')
    expect(passwordMessages.length).toBe(1)
    expect(passwordMessages.at(0).text()).toBe('Required')

    const confimPasswordMessages = wrapper.findAll('[data-test="field_password-confirm"] .v-messages__message')
    expect(confimPasswordMessages.length).toBe(1)
    expect(confimPasswordMessages.at(0).text()).toBe('Required')
  })
  
  it.each([
    // ['Required', null], // v-text-field won't validate null
    ['Required', ''],
    ['Must be at least 8 characters long', '1bA!aaa'],
    ['Must contain a number', 'bA!aaaaaaaa'],
    ['Must contain a lowercase letter', '1BA!AAAAAAAA'],
    ['Must contain an uppercase letter', '1b!aaaaaaaa'],
    ['Must contain a special character', '1bAaaaaaaaa'],
    ['Must be at least 8 characters long', '0'], // edge case
  ])('validates the password %s', async (message, password) => {
    const wrapper = await mountLocal()

    await wrapper.find('[data-test="field_username"] input').setValue('Username')
    await wrapper.find('[data-test="field_password"] input').setValue(password)

    await submitForm(wrapper)

    let passwordMessages = wrapper.findAll('[data-test="field_password"] .v-messages__message')
    expect(passwordMessages.length).toBe(1)
    expect(passwordMessages.at(0).text()).toBe(message)
  })
  
  it.each([
    // ['Required', null], // v-text-field won't validate null
    ['Required', ''],
    ['Passwords do not match', 'NotTheSame'],
    ['Passwords do not match', '0'], // edge case
  ])('validates the password confirmation %s', async (message, password) => {
    const wrapper = await mountLocal()

    await wrapper.find('[data-test="field_username"] input').setValue('Username')
    await wrapper.find('[data-test="field_password"] input').setValue('a')
    await wrapper.find('[data-test="field_password-confirm"] input').setValue(password)
    
    await submitForm(wrapper)

    let confimPasswordMessages = wrapper.findAll('[data-test="field_password-confirm"] .v-messages__message')
    expect(confimPasswordMessages.length).toBe(1)
    expect(confimPasswordMessages.at(0).text()).toBe(message)
  })

  it('submits the form when valid', async () => {
    const later = new Later()
    const repoSpy = vi.spyOn(fakeRepo, 'signup').mockImplementation(() => {
      return later
    })

    const wrapper = await mountLocal({ router })
    
    await wrapper.vm.$router.push('/join') // This will add the redirection query param
    const notifySpy = vi.spyOn(wrapper.vm.$notify, 'success')
    const pushSpy = vi.spyOn(wrapper.vm.$router, 'push').mockImplementation((path) => Promise.resolve())

    await wrapper.find('[data-test="field_username"] input').setValue('Username')
    await wrapper.find('[data-test="field_password"] input').setValue('1bA!aaaa')
    await wrapper.find('[data-test="field_password-confirm"] input').setValue('1bA!aaaa')

    // make this part of mountLocal?
    await submitForm(wrapper)

    const btn = wrapper.find('[data-test="button_submit"]')
    expect(btn.element.disabled).toBe(true)

    await later.resolve(true)
    await flushPromises()

    expect(btn.element.disabled).toBe(false)

    expect(pushSpy).toHaveBeenCalledTimes(1)
    expect(pushSpy).toHaveBeenCalledWith('/join')
    
    expect(useUserstore().user).not.toBe(null)

    expect(repoSpy).toHaveBeenCalledTimes(1)
    expect(repoSpy).toHaveBeenCalledWith({username: 'Username', password: '1bA!aaaa'})

    expect(notifySpy).toHaveBeenCalledTimes(1)
    expect(notifySpy).toHaveBeenCalledWith('Successfully registered')
  })

  it('handles failures when submiting', async () => {
    const later = new Later()
    const repoSpy = vi.spyOn(fakeRepo, 'signup').mockImplementation(() => {
      return later
    })

    const wrapper = await mountLocal()
    const pushSpy = vi.spyOn(wrapper.vm.$router, 'push').mockImplementation((path) => Promise.resolve())

    await wrapper.find('[data-test="field_username"] input').setValue('Username')
    await wrapper.find('[data-test="field_password"] input').setValue('1bA!aaaa')
    await wrapper.find('[data-test="field_password-confirm"] input').setValue('1bA!aaaa')

    const notifySpy = vi.spyOn(wrapper.vm.$notify, 'error')
    await submitForm(wrapper)

    const btn = wrapper.find('[data-test="button_submit"]')
    expect(btn.element.disabled).toBe(true)

    await later.reject('That was a junk request bro')
    await flushPromises()

    expect(btn.element.disabled).toBe(false)

    expect(pushSpy).toHaveBeenCalledTimes(0)
    
    expect(useUserstore().user).toBe(null)

    expect(repoSpy).toHaveBeenCalledTimes(1)
    expect(repoSpy).toHaveBeenCalledWith({username: 'Username', password: '1bA!aaaa'})

    expect(notifySpy).toHaveBeenCalledTimes(1)
    expect(notifySpy).toHaveBeenCalledWith('Failed to register: That was a junk request bro')
  })
})
