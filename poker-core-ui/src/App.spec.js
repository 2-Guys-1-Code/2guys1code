import { describe, it } from 'vitest'
import App from './App.vue'

const mountLocal = async (options) => {
  const wrapper = mount(App, options || {})
  await wrapper.vm.$nextTick();
  return wrapper
}

describe('App', () => {
  it('mounts', async () => {
    const wrapper = await mountLocal()
  })
})
