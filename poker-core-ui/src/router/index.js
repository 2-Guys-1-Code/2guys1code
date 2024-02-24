import { createRouter as realCreateRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

// TODO: Use constants
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: {
      authForbidden: true,
    },
  },
  {
    path: '/signup',
    name: 'signup',
    component: () => import('../views/Signup.vue'),
    meta: {
      authForbidden: true,
    },
  },
  {
    path: '/join',
    name: 'join',
    component: () => import('../views/AboutView.vue'),
    meta: {
      authRequired: true,
    },
  },
  {
    path: '/create',
    name: 'create',
    component: () => import('../views/CreateGame.vue'),
    meta: {
      authRequired: true,
    },
  },
  {
    path: '/game',
    name: 'game',
    component: () => import('../views/GameRoom.vue'),
    // meta: {
    //   authRequired: true,
    // },
  },
]

function createRouter(options, store = null) {
  options = Object.assign({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: routes
  }, options)
  const router = realCreateRouter(options)

  router.beforeEach((to, from) => {
    if (to.meta?.authRequired && store && !store.user) {
      return { name: 'login', query: { redirect: to.path } }
    } else if (to.meta?.authForbidden && store && store.user) {
      // Maybe this should prevent the navigation instead of redirecting?
      return { name: 'home' }
    } else if (to.meta?.authForbidden && from.query?.redirect && !to.query?.redirect) {
      return Object.assign(to, {
        query: { redirect: from.query.redirect }
      })
    }
  })

  return router
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
})



export default router
export {
  routes,
  createRouter
}
