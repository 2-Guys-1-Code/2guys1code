import * as helpers from '@/helpers/helpers'

import { describe, expect, it, vi } from 'vitest'

import CreateGame from '../CreateGame.vue'
import { flushPromises, DOMWrapper } from '@vue/test-utils'
import { Later } from '@/tests/helpers'

const fakeGameRepo = {
  create: (data) => Promise.resolve(data),
}

const fakeGameOptionsRepo = {
  get: () => Promise.resolve({
    gameTypes: [
      { id: '1', name: 'Texas Holdem' },
      { id: '2', name: 'Omaha' },
    ],
  }),
}

const mountLocal = async (options = {}) => {
  const wrapper = mount(CreateGame, {
    props: {
      gameRepoFactory: () => {
        return fakeGameRepo
      },
      gameOptionsRepoFactory: () => {
        return fakeGameOptionsRepo
      },
    },
    ...options
  })
  await flushPromises()
  await wrapper.vm.$nextTick();
  return wrapper
}

const submitForm = async (wrapper) => {
    await wrapper.find('[data-test="button_submit"]').trigger('click')
    await flushPromises() // wait for validation
}

describe.skip('CreateGameView', async () => {
  it('displays a field for the type of game', async () => {
    const wrapper = await mountLocal({
      attachTo: document.body
    })
    
    const field = wrapper.findComponent('[data-test="field_game-type"]')
    expect(field.vm.$props.value).toBe(null)
    await field.trigger('click')
    
    const body = new DOMWrapper(document.body);
    const options = body.findAll('[data-test="field_game-type_options"] .v-list-item')
    expect(options.length).toBe(2)
  })

  // TODO: Eventually, the game type will determine the other available options
  it('displays a field for the number of players', async () => {
    const wrapper = await mountLocal()
    expect(wrapper.find('[data-test="field_max-players"] input').element.value).toBe('9')
    expect(
      wrapper.find('[data-test="field_max-players"] input').element.attributes.disabled,
    ).toBeFalsy()
  })

  it('displays a field for the game code', async () => {
    vi.spyOn(helpers, 'makeid').mockReturnValue('AbCdEf')

    const wrapper = await mountLocal()
    expect(wrapper.find('[data-test="field_game-code"] input').element.value).toBe('AbCdEf')
    expect(
      wrapper.find('[data-test="field_game-code"] input').element.attributes.disabled,
    ).toBeTruthy()

    vi.restoreAllMocks()
  })

  it('validates the form on submit', async () => {
    // empty the nb of players field
    // submit

    // should not make the api call (spy/mock)
    // Should display the error in the form

    const wrapper = await mountLocal()
    await wrapper.find('[data-test="field_max-players"] input').setValue('')

    await submitForm(wrapper)

    let gameTypeMessages = wrapper.findAll('[data-test="field_game-type"] .v-messages__message')
    expect(gameTypeMessages.length).toBe(1)
    expect(gameTypeMessages.at(0).text()).toBe('Required')

    let maxPlayersMessages = wrapper.findAll('[data-test="field_max-players"] .v-messages__message')
    expect(maxPlayersMessages.length).toBe(1)
    expect(maxPlayersMessages.at(0).text()).toBe('Required')
  })
  
  it.each([
    // ['Required', null], // v-text-field won't validate null
    ['Required', ''],
    ['Must be 2 or more', 1],
    ['Must be 9 or less', 10],
  ])('validates the password %s', async (message, value) => {
    const wrapper = await mountLocal()

    await wrapper.find('[data-test="field_max-players"] input').setValue(value)

    await submitForm(wrapper)

    let maxPlayersMessages = wrapper.findAll('[data-test="field_max-players"] .v-messages__message')
    expect(maxPlayersMessages.length).toBe(1)
    expect(maxPlayersMessages.at(0).text()).toBe(message)
  })

  it.skip('submits the form when valid', async () => {
    const later = new Later()
    const repoSpy = vi.spyOn(fakeGameRepo, 'create').mockImplementation(() => {
      return later
    })

    // const wrapper = await mountLocal({ router })
    const wrapper = await mountLocal()
    
    // await wrapper.vm.$router.push('/join') // This will add the redirection query param
    const notifySpy = vi.spyOn(wrapper.vm.$notify, 'success')
    // const pushSpy = vi.spyOn(wrapper.vm.$router, 'push').mockImplementation((path) => Promise.resolve())

    console.log('setting value')
    await wrapper.findComponent('[data-test="field_game-type"]').vm.select({ id: '1', name: 'Texas Holdem' })
    // await wrapper.findComponent('[data-test="field_game-type"]').vm.select('1')
    // await wrapper.findComponent({name: 'VSelect'}).vm.select({ id: '1', name: 'Texas Holdem' })
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    // await wrapper.findComponent({name: 'VSelect'}).vm.select({ id: '1', name: 'Texas Holdem' })

    console.log(wrapper.findComponent({name: 'VSelect'}).vm.modelValue)

    await submitForm(wrapper)

    const btn = wrapper.find('[data-test="button_submit"]')
    expect(btn.element.disabled).toBe(true)

    await later.resolve(true)
    await flushPromises()

    expect(btn.element.disabled).toBe(false)

    // expect(pushSpy).toHaveBeenCalledTimes(1)
    // expect(pushSpy).toHaveBeenCalledWith('/join')
    
    // expect(useUserstore().user).not.toBe(null)

    expect(repoSpy).toHaveBeenCalledTimes(1)
    expect(repoSpy).toHaveBeenCalledWith({username: 'Username', password: '1bA!aaaa'})

    expect(notifySpy).toHaveBeenCalledTimes(1)
    expect(notifySpy).toHaveBeenCalledWith('Successfully registered')
  })

  // it('handles failures when submiting', async () => {
  //   const later = new Later()
  //   const repoSpy = vi.spyOn(fakeRepo, 'signup').mockImplementation(() => {
  //     return later
  //   })

  //   const wrapper = await mountLocal()
  //   const pushSpy = vi.spyOn(wrapper.vm.$router, 'push').mockImplementation((path) => Promise.resolve())

  //   await wrapper.find('[data-test="field_username"] input').setValue('Username')
  //   await wrapper.find('[data-test="field_password"] input').setValue('1bA!aaaa')
  //   await wrapper.find('[data-test="field_password-confirm"] input').setValue('1bA!aaaa')

  //   const notifySpy = vi.spyOn(wrapper.vm.$notify, 'error')
  //   await submitForm(wrapper)

  //   const btn = wrapper.find('[data-test="button_submit"]')
  //   expect(btn.element.disabled).toBe(true)

  //   await later.reject('That was a junk request bro')
  //   await flushPromises()

  //   expect(btn.element.disabled).toBe(false)

  //   expect(pushSpy).toHaveBeenCalledTimes(0)
    
  //   expect(useUserstore().user).toBe(null)

  //   expect(repoSpy).toHaveBeenCalledTimes(1)
  //   expect(repoSpy).toHaveBeenCalledWith({username: 'Username', password: '1bA!aaaa'})

  //   expect(notifySpy).toHaveBeenCalledTimes(1)
  //   expect(notifySpy).toHaveBeenCalledWith('Failed to register: That was a junk request bro')
  // })

  // wrapper.vm.selectItem('foo')

  // it('disables the submit button on submit', () => {
  //   // submit

  //   // should make the api call (spy/mock to remain pending)
  //   // Should disable the button

  //   const wrapper = mount(CreateGameView, { props: { msg: 'Hello Vitest' } })
  //   expect(wrapper.text()).toContain('Hello Vitest')
  // })

  // it('redirects to the game room', () => {
  //   // submit

  //   // should make the api call (spy/mock to succeed)
  //   // Should redirect (spy/mock the router)

  //   const wrapper = mount(CreateGameView, { props: { msg: 'Hello Vitest' } })
  //   expect(wrapper.text()).toContain('Hello Vitest')
  // })
})
