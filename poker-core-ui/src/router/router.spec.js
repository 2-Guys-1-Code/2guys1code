import { createRouter } from '.'

import { describe, expect, it, beforeAll, beforeEach } from 'vitest'
import { defineStore, setActivePinia, createPinia } from 'pinia'

const store = defineStore('test', {
    state: () => {
        return {
            user: null,
        }
    },
})

function login(store) {
    store.user = {}
}

function setTargetUrl(store) {
    store.user = {}
}

describe('router', () => {
    let router
    beforeAll(() => {
        setActivePinia(createPinia())
        router = createRouter({}, store())
    })

    beforeEach(async () => {
        await router.push('/')
        store().$reset()
    })

    it.each([
        '/join',
        '/create',
    ])('redirects to login', async (path) => {
        await router.push(path)
        expect(router.currentRoute.value.name).toBe('login')
        expect(router.currentRoute.value.query.redirect).toBe(path)
    })

    it('passes the redirect param to signup', async () => {
        await router.push('/join')
        await router.push('/signup')
        expect(router.currentRoute.value.name).toBe('signup')
        expect(router.currentRoute.value.query.redirect).toBe('/join')
    })

    it('passes the redirect param back to login', async () => {
        await router.push('/join')
        await router.push('/signup')
        await router.push('/login')
        expect(router.currentRoute.value.name).toBe('login')
        expect(router.currentRoute.value.query.redirect).toBe('/join')
    })

    it('passes the redirect param back to join', async () => {
        await router.push('/join')
        await router.push('/signup')
        await router.push('/join')
        expect(router.currentRoute.value.name).toBe('login')
        expect(router.currentRoute.value.query.redirect).toBe('/join')
    })

    it.each([
        '/',
        '/login',
        '/signup',
    ])('does not redirect to login', async (path) => {
        await router.push(path)
        expect(router.currentRoute.value.path).toBe(path)
    })

    it('does not redirect to login when user is logged in', async () => {
        login(store())
        await router.push('/create')
        expect(router.currentRoute.value.name).toBe('create')
    })

    it.each([
        '/login',
        '/signup',
    ])('redirects to home when user is logged in', async (path) => {
        login(store())
        await router.push(path)
        expect(router.currentRoute.value.name).toBe('home')
    })

    // This is probably just the job of the login / create component, not the router.
    // However, when the router redirects to login, it should also set the target url.
    // it('redirects after logging in', async () => {
    //     setTargetUrl(store())
    //     login(store())
    //     await router.push('/create')
    //     expect(router.currentRoute.value.name).toBe('create')
    // })
})


