import * as helpers from '@/helpers/helpers'

import { describe, expect, it, vi } from 'vitest'

import CreateGameView from '../CreateGameView.vue'
import i18n from '../../i18n'
import { mount } from '@vue/test-utils'
import vuetify from '../../vuetify'

describe('CreateGameView', () => {
  it('displays a field for the number of players', () => {
    const wrapper = mount(CreateGameView, {
      global: {
        plugins: [i18n, vuetify],
      },
    })
    expect(wrapper.find('[data-test="field-max-players"] input').element.value).toBe('9')
    expect(
      wrapper.find('[data-test="field-max-players"] input').element.attributes.disabled,
    ).toBeFalsy()
  })

  it('displays a field for the game code', () => {
    vi.spyOn(helpers, 'makeid').mockReturnValue('AbCdEf')

    const wrapper = mount(CreateGameView, {
      global: {
        plugins: [i18n, vuetify],
      },
    })
    expect(wrapper.find('[data-test="field-game-code"] input').element.value).toBe('AbCdEf')
    expect(
      wrapper.find('[data-test="field-game-code"] input').element.attributes.disabled,
    ).toBeTruthy()

    vi.restoreAllMocks()
  })

  it('validates the form on submit', async () => {
    // empty the nb of players field
    // submit

    // should not make the api call (spy/mock)
    // Should display the error in the form

    const wrapper = mount(CreateGameView, {
      global: {
        plugins: [i18n, vuetify],
      },
    })

    // await wrapper.setData({ maxPlayers: 8 })
    wrapper.vm.maxPlayers = null

    await wrapper.find('[data-test="button-create-game"]').trigger('click')

    expect(wrapper.find('[data-test="field-max-players"] input').element.value).toBe('9')
  })

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
