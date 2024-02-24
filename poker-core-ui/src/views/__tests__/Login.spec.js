import { describe, expect, it, vi, afterEach, beforeAll, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import Login from '../Login.vue'
import { createRouter } from '../../router'
import { useUserstore } from '@/stores/user'
import { flushPromises } from '@vue/test-utils'
import { Later } from '@/tests/helpers'

const fakeRepo = {
  login: (data) => Promise.resolve(data),
}

const mountLocal = async (options = {}) => {
  const wrapper = mount(Login, {
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

describe('Login', () => {
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
    
    let passwordField = wrapper.find('[data-test="field_password"]')

    expect(passwordField.find('input').element.type).toBe('password')
    await passwordField.find('.v-icon--clickable').trigger('click')
    expect(passwordField.find('input').element.type).toBe('text')

    await passwordField.find('.v-icon--clickable').trigger('click')
    expect(passwordField.find('input').element.type).toBe('password')
  })

  it('validates the form on submit', async () => {
    const wrapper = await mountLocal()

    await submitForm(wrapper)

    let usernameMessages = wrapper.findAll('[data-test="field_username"] .v-messages__message')
    expect(usernameMessages.length).toBe(1)
    expect(usernameMessages.at(0).text()).toBe('Required')

    let passwordMessages = wrapper.findAll('[data-test="field_password"] .v-messages__message')
    expect(passwordMessages.length).toBe(1)
    expect(passwordMessages.at(0).text()).toBe('Required')
  })
  
  it('logs in when submitting a valid form', async () => {
    const later = new Later()
    const repoSpy = vi.spyOn(fakeRepo, 'login').mockImplementation(() => later)

    const wrapper = await mountLocal({ router })
    
    await wrapper.vm.$router.push('/join') // This will add the redirection query param
    const notifySpy = vi.spyOn(wrapper.vm.$notify, 'success')
    const pushSpy = vi.spyOn(wrapper.vm.$router, 'push').mockImplementation((path) => Promise.resolve())

    await wrapper.find('[data-test="field_username"] input').setValue('U')
    // The password is not validated beyond its presence, so we don't need to set a valid password
    await wrapper.find('[data-test="field_password"] input').setValue('P')

    await submitForm(wrapper)

    const btn = wrapper.find('[data-test="button_submit"]')
    expect(btn.element.disabled).toBe(true)

    later.resolve({ username: 'U'})
    await flushPromises()

    expect(btn.element.disabled).toBe(false)

    expect(pushSpy).toHaveBeenCalledTimes(1)
    expect(pushSpy).toHaveBeenCalledWith('/join')
    
    expect(useUserstore().user).not.toBe(null)

    expect(repoSpy).toHaveBeenCalledTimes(1)
    expect(repoSpy).toHaveBeenCalledWith({username: 'U', password: 'P'})

    expect(notifySpy).toHaveBeenCalledTimes(1)
    expect(notifySpy).toHaveBeenCalledWith('Successfully signed in')
  })

  it('handles failures when submiting', async () => {
    const later = new Later()
    const repoSpy = vi.spyOn(fakeRepo, 'login').mockImplementation(() => {
      return later
    })

    const wrapper = await mountLocal()
    const pushSpy = vi.spyOn(wrapper.vm.$router, 'push').mockImplementation((path) => Promise.resolve())

    await wrapper.find('[data-test="field_username"] input').setValue('U')
    await wrapper.find('[data-test="field_password"] input').setValue('P')

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
    expect(repoSpy).toHaveBeenCalledWith({username: 'U', password: 'P'})

    expect(notifySpy).toHaveBeenCalledTimes(1)
    expect(notifySpy).toHaveBeenCalledWith('Failed to sign in: That was a junk request bro')
  })
})
