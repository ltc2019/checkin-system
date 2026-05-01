import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/', name: 'Home', component: () => import('../views/Home.vue'), meta: { auth: true } },
  { path: '/early', name: 'Early', component: () => import('../views/Early.vue'), meta: { auth: true } },
  { path: '/reading', name: 'Reading', component: () => import('../views/Reading.vue'), meta: { auth: true } },
  { path: '/sport', name: 'Sport', component: () => import('../views/Sport.vue'), meta: { auth: true } },
  { path: '/books', name: 'Books', component: () => import('../views/Books.vue'), meta: { auth: true } },
  { path: '/stats', name: 'Stats', component: () => import('../views/Stats.vue'), meta: { auth: true } },
  { path: '/rank', name: 'Rank', component: () => import('../views/Rank.vue'), meta: { auth: true } },
  { path: '/admin', name: 'Admin', component: () => import('../views/Admin.vue'), meta: { auth: true, admin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.auth && !userStore.token) {
    next('/login')
  } else if (to.meta.admin && userStore.role !== 'admin') {
    next('/')
  } else {
    next()
  }
})

export default router