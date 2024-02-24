import ResizeObserver from 'resize-observer-polyfill'
import { afterAll, beforeAll } from 'vitest';
import { mount } from '@vue/test-utils'
import i18n from '../i18n'
import vuetify from '../vuetify'
import { useNotify } from '../plugins/notify'
import { createRouter } from '../router'
// import { createTestingPinia } from '@pinia/testing'
// import { useLocale } from 'vuetify'

beforeAll(() => {
    global.ResizeObserver = ResizeObserver
    // const { current } = useLocale()
    // current.value = 'en'
});
afterAll(() => {
    // nothing for now
});

global.getMountOptions = (overrides = {}) => {
    const {
        router = createRouter(),
        notify = useNotify(),
    } = overrides
    delete overrides.router
    delete overrides.notify

    return {
        ...overrides,
        global: {
            plugins: [i18n, vuetify, router],
            mocks: {
                $router: router,
                $notify: notify,
            },
        },
    }
}
global.mount = (component, options) => {
    return mount(component, getMountOptions(options))
}